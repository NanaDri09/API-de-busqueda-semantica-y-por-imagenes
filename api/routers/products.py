import time
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse

from core.services.product_service import ProductService
from core.models.product import Product
import base64
import io
from PIL import Image, UnidentifiedImageError
from data.productos_del_json_copy import PRODUCTS_JSON

from ..models.requests import (
    ProductCreateRequest, 
    ProductUpdateRequest, 
    BatchProductCreateRequest,
    BatchDeleteRequest,
    PaginationRequest
)
from ..models.responses import (
    ProductResponseImage,
    ProductListResponse,
    BatchResponse,
    MessageResponse,
    ErrorResponse, 
    ProductResponse
)
from ..dependencies import get_product_service, get_request_id, verify_api_key
from datetime import datetime, timezone
import logging

import requests

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={
        404: {"model": ErrorResponse, "description": "Product not found"},
        409: {"model": ErrorResponse, "description": "Product already exists"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(
        dbname='Tesis',
        user='postgres', 
        password='1234',
        host='localhost',
        port='5433'
    )


def product_to_response(product: Product) -> ProductResponseImage:
    """Convert Product model to ProductResponseImage (includes image_url)."""
    return ProductResponseImage(
        id=product.id,
        title=product.title,
        description=product.description,
        image_url=product.image_url
    )

import os
from pathlib import Path
import psycopg2

@router.post("/load-from-database",
    response_model=BatchResponse,
    status_code=status.HTTP_201_CREATED)
async def load_products_from_database(
    request: Request,
    service: ProductService = Depends(get_product_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Load products from PostgreSQL database and add them to search indices."""
    request_id = get_request_id(request)
    start_time = time.time()
    
    successful = []
    failed = []
    
    db_config = {
        'dbname': 'Tesis',
        'user': 'postgres', 
        'password': '1234',
        'host': 'localhost',
        'port': '5433'
    }
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Query products from database
        cursor.execute("""
            SELECT p.id_producto, p.titulo, p.descripcion, p.image_path, p.caption
            FROM producto p
        """)
        
        products_data = cursor.fetchall()
        
        for product_row in products_data:
            try:
                product_id, title, description, image_path, caption = product_row
                
                if not all([product_id, title, description, image_path]):
                    failed.append({
                        "id": product_id or "unknown",
                        "error": "Missing required fields"
                    })
                    continue
                
                # Crear el producto directamente
                product = Product(
                    id=product_id,
                    title=title,
                    description=description,
                    image_url=image_path
                )
                
                # Agregar a todos los repositorios manualmente
                service.vector_repo.add_product(product)
                service.bm25_repo.add_product(product)
                service.image_repo.add_image(product)
                service.caption_repo.add_caption(product)
                
                successful.append(product.id)
                logger.debug(f"Successfully loaded product {product_id} from database [Request: {request_id}]")
                
            except Exception as e:
                failed.append({
                    "id": product_row[0] if product_row else 'unknown',
                    "error": f"Loading failed: {str(e)}"
                })
        
        # Save all indices
        service.vector_repo.save_index()
        service.caption_repo.save_index()
        service.image_repo.save_index()
        
        execution_time = (time.time() - start_time) * 1000
        
        return BatchResponse(
            successful=successful,
            failed=failed,
            total_processed=len(products_data),
            success_count=len(successful),
            failure_count=len(failed),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Database error: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.post("/load-from-json",
    response_model=BatchResponse,
    status_code=status.HTTP_201_CREATED)
async def load_products_from_json(
    request: Request,
    service: ProductService = Depends(get_product_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    request_id = get_request_id(request)
    start_time = time.time()
    
    successful = []
    failed = []
    
    try:
        for product_data in PRODUCTS_JSON:
            try:
                product_id = str(product_data.get('id'))
                title = product_data.get('title')
                description = product_data.get('description')
                image_path = product_data.get('image_url')
                caption = product_data.get('caption')
                
                if not all([product_id, title, description, image_path]):
                    failed.append({
                        "id": product_id or "unknown",
                        "error": "Missing required fields"
                    })
                    continue
                
                if not os.path.exists(image_path):
                    failed.append({
                        "id": product_id,
                        "error": f"Image file not found: {image_path}"
                    })
                    continue
                
                # Crear el producto directamente
                product = Product(
                    id=product_id,
                    title=title,
                    description=description,
                    image_url=image_path
                )
                
                # Agregar a todos los repositorios manualmente
                service.vector_repo.add_product(product)
                service.bm25_repo.add_product(product)
                service.image_repo.add_image(product)
                service.caption_repo.add_caption(product, caption)
                
                successful.append(product.id)
                logger.debug(f"Successfully created product {product_id} [Request: {request_id}]")
                
            except Exception as e:
                failed.append({
                    "id": product_data.get('id', 'unknown'),
                    "error": f"Creation failed: {str(e)}"
                })
        
        # Guardar todos los índices al final
        service.vector_repo.save_index()
        service.caption_repo.save_index()
        service.image_repo.save_index()
        
        execution_time = (time.time() - start_time) * 1000
        
        return BatchResponse(
            successful=successful,
            failed=failed,
            total_processed=len(PRODUCTS_JSON),
            success_count=len(successful),
            failure_count=len(failed),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", 
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product (multipart/form-data)",
    description="Create a new product with id, title, description and an image (multipart/form-data).")
async def create_product(
    request: Request,
    id: str = Form(..., min_length=1, max_length=500),
    title: str = Form(..., min_length=1, max_length=500),
    description: str = Form(..., min_length=1, max_length=5000),
    file: UploadFile = File(...),
    image_filename_hint: Optional[str] = Form(None, max_length=300),
    service: ProductService = Depends(get_product_service),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """Create a product via multipart/form-data with form fields + file."""
    request_id = get_request_id(request)
    start_time = time.time()
    conn = None
    cursor = None

    try:
        # Validar campos
        try:
            product_request = ProductCreateRequest(
                id=id,
                title=title,
                description=description,
                image_base64=None,
                image_filename_hint=image_filename_hint
            )
        except Exception as ve:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

        # Leer y validar imagen
        try:
            file_bytes = await file.read()
            image_obj = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        except UnidentifiedImageError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Uploaded file is not a valid image")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Error reading uploaded file: {e}")
        finally:
            try:
                await file.seek(0)
            except Exception:
                pass

        # Crear producto en índices
        product = service.create_product(
            id=product_request.id,
            title=product_request.title,
            description=product_request.description,
            image=image_obj
        )

        # Guardar en base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insertar producto
        cursor.execute("""
            INSERT INTO producto (id_producto, titulo, descripcion, image_path)
            VALUES (%s, %s, %s, %s)
        """, (product.id, product.title, product.description, product.image_url))
        
        # Generar embeddings
        title_embedding = service.vector_repo.embedding_service.generate_embedding(product.title)
        desc_embedding = service.vector_repo.embedding_service.generate_embedding(product.description)
        image_embedding = service.image_service._compute_image_embedding(product.image_url).flatten().tolist()
        
        # Generar caption y su embedding
        caption = service.image_service.generar_descripcion_imagen(product.image_url)
        caption_embedding = service.vector_repo.embedding_service.generate_embedding(caption) if caption else None
        
        # Insertar embeddings
        cursor.execute("""
            INSERT INTO embeddings (id_producto, embedding_titulo, embedding_descripcion, embedding_imagen, embedding_caption)
            VALUES (%s, %s, %s, %s, %s)
        """, (product.id, title_embedding, desc_embedding, image_embedding, caption_embedding))
        
        conn.commit()

        execution_time = (time.time() - start_time) * 1000
        logger.info(f"Successfully created product {product.id} in {execution_time:.1f}ms [Request: {request_id}]")
        return product_to_response(product)

    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except ValueError as ve:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error creating product: {e} [Request: {request_id}]")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error occurred")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

        
@router.get("/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Retrieve a specific product by its unique identifier.")
async def get_product(
    product_id: str,
    request: Request,
    service: ProductService = Depends(get_product_service)
):
    """Get a product by ID."""
    request_id = get_request_id(request)
    
    logger.info(f"Retrieving product {product_id} [Request: {request_id}]")
    
    product = service.get_product_by_id(product_id)
    if not product:
        logger.warning(f"Product {product_id} not found [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found"
        )
    
    return product_to_response(product)


@router.put("/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    description="Update an existing product's title and/or description. The product will be re-indexed automatically.")
async def update_product(
    product_id: str,
    request: Request,
    title: Optional[str] = Form(None, min_length=1, max_length=500),
    description: Optional[str] = Form(None, min_length=1, max_length=5000),
    file: Optional[UploadFile] = File(None),  
    image_filename_hint: Optional[str] = Form(None, max_length=300),
    service: ProductService = Depends(get_product_service),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """Update an existing product."""
    request_id = get_request_id(request)
    conn = None
    cursor = None
    
    try:
        logger.info(f"Updating product {product_id} [Request: {request_id}]")
        product = service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID '{product_id}' not found")

        # Usar valores existentes si no se proporcionan nuevos
        if title is None:
            title = product.title
        if description is None:
            description = product.description   

        image_obj = None
        image_url = product.image_url

        if file is not None:
            try:
                file_bytes = await file.read()
                image_obj = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            except Exception as e:
                logger.warning(f"Invalid uploaded file for product update {product_id}: {e} [Request: {request_id}]")
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Uploaded file is not a valid image")
        else:
            # Si no hay archivo, usar imagen existente
            if product.image_url and product.image_url.startswith(('http://', 'https://')):
                try:
                    logger.info(f"Using existing image URL for product {product_id}: {product.image_url} [Request: {request_id}]")
                    resp = requests.get(product.image_url, timeout=10)
                    resp.raise_for_status()
                    image_bytes = resp.content
                    image_obj = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                except Exception as e:
                    logger.warning(f"Failed to download existing image for product {product_id}: {e} [Request: {request_id}]")
                    image_obj = None
            else:
                logger.info(f"No image update for product {product_id} [Request: {request_id}]")
                image_obj = None

        # Actualizar en índices
        updated_product = service.update_product(
            id=product_id,
            title=title,
            description=description,
            image=image_obj
        )

        # Actualizar en base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Actualizar producto
        cursor.execute("""
            UPDATE producto 
            SET titulo = %s, descripcion = %s, image_path = %s
            WHERE id_producto = %s
        """, (updated_product.title, updated_product.description, updated_product.image_url, product_id))
        
        # Regenerar embeddings
        title_embedding = service.vector_repo.embedding_service.generate_embedding(updated_product.title)
        desc_embedding = service.vector_repo.embedding_service.generate_embedding(updated_product.description)
        
        # Actualizar embeddings de texto
        cursor.execute("""
            UPDATE embeddings 
            SET embedding_titulo = %s, embedding_descripcion = %s
            WHERE id_producto = %s
        """, (title_embedding, desc_embedding, product_id))
        
        # Si hay nueva imagen, actualizar embedding de imagen y caption
        if image_obj:
            image_embedding = service.image_service._compute_image_embedding(updated_product.image_url).flatten().tolist()
            caption = service.image_service.generar_descripcion_imagen(updated_product.image_url)
            caption_embedding = service.vector_repo.embedding_service.generate_embedding(caption) if caption else None
            cursor.execute("""
                UPDATE embeddings 
                SET embedding_imagen = %s, embedding_caption = %s
                WHERE id_producto = %s
            """, (image_embedding, caption_embedding, product_id))
        
        conn.commit()

        logger.info(f"Successfully updated product {product_id} [Request: {request_id}]")
        return product_to_response(updated_product)

    except ValueError as e:
        if conn:
            conn.rollback()
        logger.warning(f"Product update failed: {e} [Request: {request_id}]")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error updating product: {e} [Request: {request_id}]", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error occurred")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@router.delete("/{product_id}",
    response_model=MessageResponse,
    summary="Delete product",
    description="Delete a product by its ID. The product will be removed from all search indexes.")
async def delete_product(
    product_id: str,
    request: Request,
    service: ProductService = Depends(get_product_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Delete a product."""
    request_id = get_request_id(request)
    conn = None
    cursor = None
    
    try:
        logger.info(f"Deleting product {product_id} [Request: {request_id}]")
        
        # Verificar que el producto existe
        product = service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID '{product_id}' not found"
            )
        
        # Eliminar de índices
        success = service.delete_product(product_id)
        if not success:
            logger.warning(f"Product {product_id} not found for deletion [Request: {request_id}]")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID '{product_id}' not found"
            )
        
        # Eliminar de base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Eliminar embeddings primero (por foreign key)
        cursor.execute("DELETE FROM embeddings WHERE id_producto = %s", (product_id,))
        
        # Eliminar producto
        cursor.execute("DELETE FROM producto WHERE id_producto = %s", (product_id,))
        
        conn.commit()
        
        logger.info(f"Successfully deleted product {product_id} [Request: {request_id}]")
        return MessageResponse(
            message=f"Product '{product_id}' deleted successfully",
            timestamp=datetime.now(timezone.utc)
        )
        
    except ValueError as e:
        if conn:
            conn.rollback()
        logger.warning(f"Product deletion failed: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error deleting product: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/",
    response_model=ProductListResponse,
    summary="List products",
    description="Get a paginated list of all products in the system.")
async def list_products(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    service: ProductService = Depends(get_product_service)
):
    """List all products with pagination."""
    request_id = get_request_id(request)
    
    logger.info(f"Listing products (page={page}, size={size}) [Request: {request_id}]")
    
    try:
        # Get all products
        all_products = service.list_all_products()
        total = len(all_products)
        
        # Calculate pagination
        total_pages = math.ceil(total / size) if total > 0 else 1
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        
        # Get page of products
        page_products = all_products[start_idx:end_idx]
        
        # Convert to response models
        product_responses = [product_to_response(product) for product in page_products]
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error listing products: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.post("/batch",
    response_model=BatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Batch create products",
    description="Create multiple products in a single request for better performance.")
async def batch_create_products(
    batch_request: BatchProductCreateRequest,
    request: Request,
    service: ProductService = Depends(get_product_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Batch create multiple products."""
    request_id = get_request_id(request)
    start_time = time.time()
    
    logger.info(f"Batch creating {len(batch_request.products)} products [Request: {request_id}]")
    
    successful = []
    failed = []
    
    try:
        # Convert to format expected by service
        products_data = [
            {
                "id": product.id,
                "title": product.title,
                "description": product.description
            }
            for product in batch_request.products
        ]
        
        # Use batch creation for better performance
        try:
            created_products = service.batch_create_products(products_data)
            successful = [product.id for product in created_products]
            
        except Exception as e:
            # If batch fails, try individual creation
            logger.warning(f"Batch creation failed, trying individual creation: {e}")
            
            for product_req in batch_request.products:
                try:
                    created_product = service.create_product(
                        id=product_req.id,
                        title=product_req.title,
                        description=product_req.description
                    )
                    successful.append(created_product.id)
                except Exception as individual_error:
                    failed.append({
                        "id": product_req.id,
                        "error": str(individual_error)
                    })
        
        execution_time = (time.time() - start_time) * 1000
        
        logger.info(f"Batch creation completed: {len(successful)} successful, {len(failed)} failed [Request: {request_id}]")
        
        return BatchResponse(
            successful=successful,
            failed=failed,
            total_processed=len(batch_request.products),
            success_count=len(successful),
            failure_count=len(failed),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in batch creation: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.delete("/batch",
    response_model=BatchResponse,
    summary="Batch delete products",
    description="Delete multiple products in a single request.")
async def batch_delete_products(
    batch_request: BatchDeleteRequest,
    request: Request,
    service: ProductService = Depends(get_product_service),
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Batch delete multiple products."""
    request_id = get_request_id(request)
    start_time = time.time()
    
    logger.info(f"Batch deleting {len(batch_request.product_ids)} products [Request: {request_id}]")
    
    successful_ids = []
    failed = []
    
    try:
        for product_id in batch_request.product_ids:
            try:
                success = service.delete_product(product_id)
                if success:
                    successful_ids.append(product_id)
                else:
                    failed.append({
                        "id": product_id,
                        "error": "Product not found"
                    })
            except Exception as e:
                failed.append({
                    "id": product_id,
                    "error": str(e)
                })
        
        execution_time = (time.time() - start_time) * 1000
        
        logger.info(f"Batch deletion completed: {len(successful_ids)} successful, {len(failed)} failed [Request: {request_id}]")
        
        return BatchResponse(
            successful=successful_ids,
            failed=failed,
            total_processed=len(batch_request.product_ids),
            success_count=len(successful_ids),
            failure_count=len(failed),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in batch deletion: {e} [Request: {request_id}]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        ) 