from PIL import Image


PRODUCTS_JSON = [
  {
    "id": "63",
    "title": "APlus Batería 12V/7A",
    "description": "APlus Batería 12V/7A",
    "image_url": "Imagenes/1.png",
    "caption": "The image displays a black battery with red accents and a red logo that says \"APlus.\" The battery is situated against a plain, white background, and no other objects or distractions are present, giving the image a simple and minimalist appearance."
  },
  {
    "id": "66",
    "title": "APlus UPS Backup 600VA para PC escritorio",
    "description": "UPS Backup de 600VA, marca Aplus para PC escritorio.",
    "image_url": "Imagenes/2.png",
    "caption": "The image depicts a black UPS (uninterruptible power supply) device placed against a white background. The UPS has a rectangular structure and features multiple power outlets and USB ports on its front panel. Two green indicator lights are illuminated on the front, suggesting that the device is powered on and operational. A power cord is plugged into the device. The clean, white background provides a minimalistic and straightforward visual context, emphasizing the UPS as the primary focus of the image."
  },
  {
    "id": "94",
    "title": "APlus PlusGuard 4-30A Protector de Voltaje Alambrado 30A 110V",
    "description": "APlus PlusGuard 4-30A Protector de Voltaje Alambrado 30A 110V",
    "image_url": "Imagenes/3.png",
    "caption": "The image features a rectangular black router with a simple and functional design. The router is placed on a clean white background. Its surface has a sleek appearance, and the brand name is printed in white text at the top of the device. Several USB ports are visible on the router, contributing to its functionality. The overall composition highlights the router as the main focus of the image."
  },
  {
    "id": "101",
    "title": "MAXELL BATERÍA ALCALINA AAA 2PK BLISTER LR03",
    "description": "BATERÍA ALCALINA AAA 2PK BLISTER LR03",
    "image_url": "Imagenes/4.png",
    "caption": "The image depicts a package of AAA alkaline batteries containing two batteries arranged side by side. The packaging features a blue and white color scheme, with the Maxell logo displayed prominently. This is a blister pack designed for consumer convenience. The overall presentation emphasizes functionality and quality, highlighting the suitability of the batteries for electronic devices such as remote controls, toys, and small appliances. The image has a simple and clean aesthetic, set against a white background."
  },
  {
    "id": "104",
    "title": "Batería alcalina tipo C  Maxell 2pk LR14",
    "description": "BATERÍA ALCALINA TIPO C 2PK LR14",
    "image_url": "Imagenes/5.png",
    "caption": "The image shows a single blue and gold colored battery placed on a white background. The brand name \"Maxell\" is prominently displayed, underlined, on the body of the battery, along with the word \"ALKALINE.\" It is a C-type battery, commonly used in medium-sized electronic devices. The composition is straightforward, with the battery centered and accompanied by a subtle shadow underneath."
  },
  {
    "id": "220",
    "title": "Maxell 6LF22-6LR61 1PK Batería Alcalina",
    "description": "Batería alcalina de alto rendimiento",
    "image_url": "Imagenes/6.png",
    "caption": "The image displays a 9V battery standing upright on a plain white surface. The battery has a blue and gold color scheme, with the brand name \"MAXELL\" prominently written in dark blue. The front of the battery features additional text, including the word \"ALKALINE\" in black and the voltage \"9V\" in blue below it. The top of the battery has a metallic clip. The overall composition of the image is simple, with a minimalistic aesthetic drawing attention to the battery as the primary focus."
  },
  {
    "id": "223",
    "title": "Maxell LR20 2PK Batería Alcalina",
    "description": "Batería alcalina de tamaño LR20, paquete de 2 unidades",
    "image_url": "Imagenes/7.png",
    "caption": "The image shows two cylindrical batteries placed side by side against a white background. The batteries have a blue and gold color scheme. Their labels prominently display \"MAXELL\" and \"ALKALINE,\" indicating the brand and battery type, along with other details such as \"D SIZE.\" The batteries appear unused and show insulating covers on their tops, suggesting they are ready for storage or future use."
  },
  {
    "id": "262",
    "title": "Bateria alcalina AAA Maxell 5PK 1,5v",
    "description": "Batería alcalina de tamaño AAA, paquete de 5 unidades, 1,5 V",
    "image_url": "Imagenes/8.png",
    "caption": "The image displays two Maxell Alkaline AAA batteries placed side by side against a clean white background. Each battery features a blue, gold, and white design, with the text \"MAXELL\" written in large blue letters and the word \"alkaline\" written in smaller white letters below it. The batteries are clearly visible, with their size indicated as AAA."
  },
  {
    "id": "265",
    "title": "Bateria Alcalina AA Maxell 2PK LR6",
    "description": "Bateria alcalina duradera de tamaño LR6",
    "image_url": "Imagenes/9.png",
    "caption": "The image depicts two Maxell brand AA batteries made of alkaline material. The batteries have a blue and gold color scheme and are placed on a clean, white background. The composition is simple, with no other objects or distractions, emphasizing the batteries as the focal point."
  },
  {
    "id": "274",
    "title": "Batería AGM, Upower,12V 7A MU-UPS 7 2-12S F1 segurity (2)",
    "description": "Bateria upowe AGM de 12 V, 7 Ah, modelo MU-UPS 7 con configuración 2-12S.",
    "image_url": "Imagenes/10.png",
    "caption": "The image features a green lithium battery branded as \"LI-Power.\" The battery appears to have the model designation \"UP7.2-12 F1.\" Based on the information provided, the battery has specifications including a voltage of 12V and a capacity of 7.2Ah. There are markings and texts on the exterior of the battery that describe its specifications, but no additional text from the image is available to confirm further details. The battery has a clean and structured appearance, indicating that it is likely designed for rechargeable use. Its exterior also includes icons and symbols, such as a recycle icon, emphasizing environmental recycling considerations. The battery is visually distinctive due to its bold green coloration."
  },
  {
    "id": "308",
    "title": "Sistema Solar Hibrido 5KW",
    "description": "Kit  solar kW: 5 paneles bifaciales de 610 W, Inversor hibrido 5kW y tensión 110v/220v.",
    "image_url": "Imagenes/11.png",
    "caption": "The image depicts a hybrid solar power system displayed against a white background. The primary components of the system include a solar panel, batteries, an inverter, and solar cables. The solar panel occupies a prominent position in the image and is white in color. Some text, such as \"Hybrid 3-30kW,\" is visible on or near the panel. The system includes several sets of red and black solar cables, which are connected to the components. Two sets of batteries are positioned near the bottom right corner, with possible branding visible, though not fully legible. The setup is arranged in an organized and minimalistic fashion, highlighting the system's clean energy focus."
  },
  {
    "id": "84",
    "title": "Taurus Turbo 1000 Ventilador",
    "description": "Ventilador 16\" 30% más aire 127V 45W",
    "image_url": "Imagenes/12.png",
    "caption": "The image displays a black 16-inch standing fan with five curved blades arranged in a circular pattern. The fan is mounted on a tall black stand, which includes a base for stability. The entire fan is set against a plain white background, making its features stand out distinctly."
  },
  {
    "id": "166",
    "title": "Taurus Austros Ventilador de Pedestal 16''",
    "description": "Ventilador 16\" tres velocidades, menos ruido",
    "image_url": "Imagenes/13.png",
    "caption": "The image depicts a standing electric fan with a round white head and silver blades mounted on a three-legged stand. The stand is primarily white and features a silver accent. The fan is placed at an angle and is set against a plain white background, creating a minimalist and clean look."
  },
  {
    "id": "233",
    "title": "Ventilador de Techo Negro y dorado Royal 56¨",
    "description": "Ventilador de Techo Negro y dorado, marca Royal de 56¨",
    "image_url": "Imagenes/14.png",
    "caption": "The image shows a stylish ceiling fan with a modern design, mounted on a white ceiling. The fan features black blades and a gold-colored central motor. An integrated light bulb in the center of the fan is turned on, emitting a warm yellowish glow that adds to the comfortable and elegant ambiance of the room. The combination of gold and black elements emphasizes the contemporary style of the fan while maintaining a sleek and polished look."
  },
  {
    "id": "268",
    "title": "Taurus Silent Power Ventilador",
    "description": "Ventilador de 18\"Pedestal y soporte de pared, potencia 75W TECNOLOGÍA ECOJET.",
    "image_url": "Imagenes/15.png",
    "caption": "The image shows a black pedestal fan standing against a plain white background. The fan has a circular metal grill encasing its spinning blades, which appear to be standard in size and shape for such models. The fan is mounted on a vertical pedestal connected to a round weighted base, which provides stability. The design appears streamlined and functional, likely suitable for oscillation to provide air circulation. The overall appearance conveys simplicity and modern utility, with the black and metallic tones contrasting with the white background."
  },
  {
    "id": "167",
    "title": "Taurus Stardust Ventilador",
    "description": "Ventilador compacto con diseño elegante y flujo de aire eficiente",
    "image_url": "Imagenes/16.png",
    "caption": "The image displays a standing electric fan with a sleek design. It has a silver metallic stand and a circular base providing support. The fan body is predominantly white, with black accents. Its blades are partially visible, enclosed within a protective frame. The overall design is minimalistic and modern."
  },
  {
    "id": "277",
    "title": "Aire Acondicionado Selectron tipo Split 12000 BTU",
    "description": "Aire Acondicionado Selectron tipo Split 12000 BTU",
    "image_url": "Imagenes/17.png",
    "caption": "The image shows a white air conditioner unit, branded as \"ROYAL,\" with the brand name prominently displayed in blue text on the casing. The unit includes a grey, round fan with visible spiral blades, integrated into the device. The casing is metallic and functional in design, emphasizing simplicity. There is a label or sticker related to energy use located on the unit, though text details on it are not visible. The air conditioner appears to be photographed against a neutral white background."
  },
  {
    "id": "291",
    "title": "PROTECTOR VOLTAJE 30A I-527 MOLD (220 V) Aplus",
    "description": "PROTECTOR VOLTAJE 30A (220 V)",
    "image_url": "Imagenes/18.png",
    "caption": "The image displays a white electronic device, rectangular in shape, with a clean, front-facing view against a white background. The device has a digital display panel, likely used to show readings such as voltage. Below or adjacent to the display are a few buttons for operation or configuration. The center of the device features a logo, and the overall design is clean and minimalist, suggesting it might be an energy meter used for household or electronic applications."
  },
  {
    "id": "11",
    "title": "PREMIER LAVADORA SEMI-AUTOMATICA 6KG.",
    "description": "LAVADORA SEMI-AUTOMATICA 6KG. Doble tina, centrifugado 4Kg,",
    "image_url": "Imagenes/19.png",
    "caption": "The image shows a white and blue portable washing machine displayed against a white background. The washing machine features a white body with a blue lid. On the top of the machine, there appear to be control knobs. The overall design of the image focuses on simplicity and clarity."
  },
  {
    "id": "13",
    "title": "PREMIER SOPORTE DE PARED PARA TV (32\" - 80\").",
    "description": "SOPORTE DE PARED PREMIER funcional para televisores (32\" - 80\").",
    "image_url": "Imagenes/20.png",
    "caption": "The image shows a black TV wall mount positioned against a plain white background. The mount is made of metal with a sleek, durable finish. It features an articulating design, including a swiveling arm that allows for full-motion adjustments such as tilting the mounted TV up, down, left, or right. The mount is suited for flat-panel TVs within a broad size range and provides structural support tailored for a variety of wall installations. The functional mechanisms of the mount are clearly visible, with the arm extended to showcase its adjustability. No other objects or text are present in the image, directing full attention to the wall mount's design and build."
  },
  {
    "id": "32",
    "title": "SELECTRON TV 50\" 4K SMART ISDBT BLUETOOTH, ANDROID 11.",
    "description": "Televisor de 50\",  resolución 4K  SMART.Androide 11",
    "image_url": "Imagenes/21.png",
    "caption": "The image shows a promotional advertisement for a 50-inch Hisense smart TV. The screen of the TV prominently displays a woman surfing on a white surfboard in the ocean. She is standing upright on the surfboard, with her right arm raised toward the sky and her left knee slightly bent, suggestive of active motion as she rides a wave. She is wearing a black swimsuit, and the bright blue sky and calm sea in the background create a vivid and serene atmosphere. The confident expression and dynamic pose of the woman add to the visually engaging scene. Additional information about the TV, including features like \"Smart TV,\" \"4K Ultra HD,\" \"WiFi,\" and \"5GHz,\" is mentioned in a detailed layout, possibly placed to the side of the advertisement."
  },
  {
    "id": "33",
    "title": "TV SELECTRON  65\" 4K SMART ISDBT BLUETOOTH, ANDROID 11.",
    "description": "SELECTRON TV 65\" 4K SMART ISDBT BLUETOOTH, ANDROID 11.",
    "image_url": "Imagenes/22.png",
    "caption": "The image depicts a 65-inch 4K Android smart TV being showcased in a promotional or advertising setting. The TV screen displays a background image of an ocean scene with curling waves, emphasizing the vivid detail afforded by the TV's 4K resolution. The screen highlights compatibility with multiple popular streaming platforms, including the logos of YouTube, Netflix, Amazon Prime Video, and Disney+. These logos are arranged neatly within the display interface, showcasing the smart TV's functionality and entertainment options. The TV has thin black borders and is supported by legs at the bottom. Overall, the composition of the image draws attention to the TV's high-definition display, smart features, and access to well-known streaming services."
  },
  {
    "id": "34",
    "title": "SELECTRON TV 43\" FHD SMART ISDBT BLUETOOTH, ANDROID 11.",
    "description": "SELECTRON TV 43\" FHD SMART ISDBT BLUETOOTH, ANDROID 11.",
    "image_url": "Imagenes/23.png",
    "caption": "The image shows a flat-screen smart TV displaying a vibrant surfing scene. On the screen, a man dressed in black is standing in the ocean, holding a surfboard. The ocean's blue waves and a sky with some clouds fill the background of the display. On the left side of the image, there is text that reads \"43 SLE-43E01 SMART TV FULL HD,\" which appears to refer to the TV's specifications. The TV is supported by a sleek two-legged stand."
  },
  {
    "id": "111",
    "title": "Taurus Hair Pro Cortador De Pelo",
    "description": "Taurus Hair Pro Cortador De Pelo",
    "image_url": "Imagenes/24.png",
    "caption": "The image shows a black Taurus hair clipper placed on a white background. The clipper features a streamlined design with grooves on its body for grip. The Taurus logo is prominently displayed on the clipper. It has a round handle and comes with a black blade. The device is connected to a black power cord, emphasizing its functionality as an electric appliance. The minimalistic white background draws attention to the hair clipper's design and features."
  },
  {
    "id": "123",
    "title": "Taurus Lanche Max 2 Sandwichera 2 Panes",
    "description": "Sandwichera de 2 Panes marca Taurus Lanche Max 2. Practica y compacta",
    "image_url": "Imagenes/25.png",
    "caption": "The image shows a white, plastic electric appliance, likely a sandwich toaster, placed against a white background. The appliance has a compact, square-shaped design with a smooth exterior. Notable features include two buttons on the top, one red and one green, positioned near a corner of the appliance. The clean, minimalist composition emphasizes the simplicity and user-friendly design of the product."
  },
  {
    "id": "126",
    "title": "Taurus Leonis Tostador Inoxidable de Pan",
    "description": "Taurus Leonis Tostador Inoxidable de Pan",
    "image_url": "Imagenes/26.png",
    "caption": "The image shows a stainless steel and black toaster with two slots for toasting bread. The toaster has the word \"Taurus\" prominently displayed on it, and it features a control mechanism on the side. The toaster is placed against a plain white background, which emphasizes its design."
  },
  {
    "id": "129",
    "title": "Taurus Remoline Batidora de Inmersión",
    "description": "Taurus Remoline Batidora de Inmersión",
    "image_url": "Imagenes/27.png",
    "caption": "The image depicts a simple and clean white hand-held immersion blender branded by Taurus, positioned on a white background. The blender has a single control button located on its housing. Accompanying the blender is a detachable blending cup, which appears to be made of white or clear plastic and includes a printed Taurus logo. Additional accessories, such as a blending stick and possibly a blending lid or attachment, are also visible. The overall arrangement conveys a minimalist and functional design."
  },
  {
    "id": "139",
    "title": "Selectron TV 32\" Smart TV",
    "description": "TELEVISOR SELECTRON SLE-32E00 SMART TV 32″ HD ANDROID 13.",
    "image_url": "Imagenes/28.png",
    "caption": "The image shows a promotional display for a smart TV. The main visual features a man standing on or posing with a bicycle against a backdrop of a blue sky with thin clouds, giving the scene a peaceful and leisurely atmosphere. The promotional details for the TV, including its specifications and model, are visible on the left side of the screen in white text over a blue rectangle. The scene is designed to evoke a sense of enjoyment and harmony with the outdoors."
  },
  {
    "id": "141",
    "title": "Royal Olla Reina",
    "description": "Royal Olla de presión eléctrica 6L Reina",
    "image_url": "Imagenes/29.png",
    "caption": "The image shows an electric pressure cooker with a black and stainless steel design, displayed on a white background. The cooker features a black plastic lid with a silver rim and a black handle on top. The body of the cooker is primarily made of stainless steel, while additional black plastic elements, such as knobs on the front, are present for controlling its settings. The product is depicted in a clean, straightforward manner, emphasizing its functional and modern design."
  },
  {
    "id": "147",
    "title": "Premier Cafetera Eléctrica",
    "description": "Premier Cafetera para Expreso Eléctrica 6 Tazas. Modelo: CM-8499",
    "image_url": "Imagenes/30.png",
    "caption": "The image depicts a black electric coffee maker placed against a solid white background. The coffee maker has a smooth, shiny surface and a traditional pot-like design. It features a spout on the right and a handle on the left. A red indicator light is visible on the body of the coffee maker. The overall appearance contrasts sharply with the clean, minimalist white background."
  },
  {
    "id": "149",
    "title": "TAURUS EVAN LICUADORA",
    "description": "Licuadora compacta y potente, ideal para preparar batidos y purés diarios.",
    "image_url": "Imagenes/31.png",
    "caption": "The image displays a white and grey Taurus-brand blender with a rectangular base and a cylindrical top featuring a transparent jar. The lower portion of the blender displays four buttons arranged in a row, indicating control options. The background is entirely white, and the scene is minimalistic, conveying a sense of cleanliness and functionality. The blender appears to be in an unused state."
  },
  {
    "id": "158",
    "title": "Taurus Citrix Exprimidor de Jugos con Jarra De Vidrio",
    "description": "Exprimidor de cítricos y jugos con jarra de vidrio.",
    "image_url": "Imagenes/32.png",
    "caption": "The image displays a Taurus Citrix electric citrus press against a clean white background. The juicer features a design with black and orange elements, including an orange-colored cone or handle and a black and orange base. A transparent cup with a handle is positioned below the press, integrated into its design. A power cable extends from the right side of the juicer, indicating its electric functionality. The brand name \"Taurus\" and the product name \"CITRIX\" are visible on the press, emphasizing its branding. The overall scene is minimalist, focusing entirely on the modern and functional aesthetic of the juicer."
  },
  {
    "id": "178",
    "title": "REGLETA CON PROTECTOR DE VOLTAJE Y USB",
    "description": "Regleta de enchufes con protector de sobretensión y puerto(s) USB integrados.",
    "image_url": "Imagenes/33.png",
    "caption": "The image shows a black power strip with multiple outlets and two USB ports. The outlets are arranged in rows, and a single plug is connected to the power strip. A red light is illuminated on the power strip, located towards the upper right portion of the device. The power strip is placed on a plain background, which emphasizes its dark color and design. The connected plug is attached to a cord that extends to the side of the image."
  },
  {
    "id": "253",
    "title": "LAVADORA SEMI AUTOMATICA, MILEXUS, ML-WM-7KGS",
    "description": "Lavadora semiautomática Milexus ML-WM-7KGS, capacidad de 7 kg",
    "image_url": "Imagenes/34.png",
    "caption": "The image displays a compact, white, portable washing machine branded \"Milexus.\" The brand name is written in blue on the machine, accompanied by the text \"Clean & Soft.\" The machine has a transparent, circular top lid, revealing compartments for washing. The design includes buttons and control panels integrated on the top of the machine. The washing machine is positioned on four small wheels. It is placed on a white floor, contributing to a clean and minimalist aesthetic."
  },
  {
    "id": "271",
    "title": "Taurus Juliette Secadora de Cabello",
    "description": "Secadora de Cabello Marca Taurus modelo Juliette.",
    "image_url": "Imagenes/35.png",
    "caption": "The image displays a compact, dark purple hair dryer positioned on a white background. The device features a rounded body design with a matching purple nozzle attached to the front. The brand name \"Taurus\" is visible in white font on the body of the hair dryer. The overall design reflects a compact size, indicating it may be intended for travel use. A white electrical cord is connected to the handle, emphasizing its functionality and usability. The clean and minimalistic purple and white color scheme adds a sense of simplicity and practicality to the product."
  },
  {
    "id": "280",
    "title": "Hidro Lavadora COOFIX 1400PSI",
    "description": "idrolavadora COOFIX de alta presión 1400 PSI, ideal para limpieza de terrazas.",
    "image_url": "Imagenes/36.png",
    "caption": "The image shows a yellow and black portable electric high-pressure washer, prominently displaying the brand name \"COOFIX\" in bold black letters on its body. The washer features a sturdy black handle for easy transport, designed with a practical ergonomic shape. A black hose is attached on one side of the washer, adding to its functionality. The clean, isolated product is placed against a white background, emphasizing its design and portability."
  },
  {
    "id": "283",
    "title": "Premier Bomba de Agua 1HP",
    "description": "Bomba de Agua de 1HP Marca Premier, altura máxima de impulso 48m",
    "image_url": "Imagenes/37.png",
    "caption": "The image depicts a blue electric water pump positioned against a plain white background. The pump is the primary focus of the image, taking up the majority of the frame. It features a round blue housing as its main body and includes a prominent black button on its surface, which appears to function as a start/stop control. A white label with black writing is visible on the housing, potentially indicating specific information like the brand or model number. The pump is displayed at a slight angle that effectively showcases its key components. Overall, the image emphasizes the clean and well-maintained appearance of the pump, with no other distracting elements in view."
  },
  {
    "id": "284",
    "title": "CR-Turbo Bomba de Agua 1/2 HP, 110V/60Hz",
    "description": "Bomba de agua CR-Turbo de 1/2 HP, compatible con 110V/60Hz",
    "image_url": "Imagenes/38.png",
    "caption": "The image shows a black electric pump placed on a white background. The pump is presented at a three-quarter angle, with the motor housing visible on the right side and what appears to be a discharge nozzle on the left. The pump includes additional components connected via cords or hoses. It has a sturdy appearance with a mounting base and some metallic elements around its structure, suggesting durable construction. The overall design implies a functional device, possibly intended for water flow or related applications."
  },
  {
    "id": "287",
    "title": "ROYAL RFH35 NEVERA HORIZONTAL 3,5 PIES - 100L",
    "description": "NEVERA HORIZONTAL 3,5 PIES - 100L, marca ROYAL, modelo RFH35.",
    "image_url": "Imagenes/39.png",
    "caption": "The image shows a white chest freezer with its lid open. The freezer has a smooth white interior and features distinct compartments, which appear to contain small items. It is positioned against a white background, creating a clean and minimalist aesthetic."
  },
  {
    "id": "289",
    "title": "ROYAL RWA090 LAVADORA AUTOMATICA 9KG",
    "description": "-Lavadora automática de 9 kilos, ahorra agua y energía.",
    "image_url": "Imagenes/40.png",
    "caption": "The image shows a portable, top-loading washing machine with a black and silver design. The washer is displayed against a plain white background, emphasizing its features in a clean and simple setting."
  },
  {
    "id": "293",
    "title": "REGLETA CON PROTECCION DE SOBRECARGA 10A, 4 SALIDAS, CABLE DE 1 M",
    "description": "APlus PlusExtend 1-10A-10M Regleta con Protección de Sobrecarga.",
    "image_url": "Imagenes/41.png",
    "caption": "The image shows a black power strip with a total of four sockets. The sockets are arranged neatly on the surface of the device. The power strip appears to be clean and functional, and it is pictured against a plain background."
  },
  {
    "id": "303",
    "title": "Caja decodificadora HH JD-TVB-202201",
    "description": "Caja descodificadora alta definición, 90-264V/60hz, control remoto, cable HDMI",
    "image_url": "Imagenes/42.png",
    "caption": "The image shows a black, rectangular device with a simple and technical design, set against a white background. The device features USB and HDMI ports, as well as other output interfaces, potentially for analog or coaxial connections. Minimalistic text or branding, such as \"TP-Link\" or references to a \"digital to analog converter,\" is present on the top surface of the device, indicating its purpose in data or signal transmission. The overall design of the device is compact and practical."
  },
  {
    "id": "24",
    "title": "APC Back-UPS BVN650M1 BATTERY BACKUP & SURGE PROTECTOR.",
    "description": "APC Back-UPS BVN650M1 BATTERY BACKUP & SURGE PROTECTOR.",
    "image_url": "Imagenes/43.png",
    "caption": "The image depicts an APC-branded black uninterruptible power supply (UPS) device resting on a beige or cream carpeted floor. The device is equipped with multiple power outlets on its top surface, including rectangular ones arranged in distinct rows. A black cable is connected to the device and is routed from its side or back, extending outward, with part of it forming a loop. The device appears to be slightly off-centered in the image and is intended for household or office use as a backup power source for electronic devices."
  },
  {
    "id": "22",
    "title": "PROCESADOR INTEL COREI3-10105 (CACHÉ DE 6M, HASTA 4.4 GHz).",
    "description": "PROCESADOR INTEL COREI3-10105 (CACHÉ DE 6M, HASTA 4.4 GHz).",
    "image_url": "Imagenes/44.png",
    "caption": "The image displays an Intel Core i3 processor along with its packaging and cooling components, neatly arranged against a plain white background. The packaging is a blue box featuring the \"Intel Core i3\" logo in white font. Beside the box, the processor is placed next to a black heatsink with copper heat pipes and a silver fan. The scene is minimalistic and orderly, with the focus clearly on the showcased items."
  },
  {
    "id": "23",
    "title": "COMBO TECLADO RATON LOGITECH MK120 USB NEGRO",
    "description": "Logitech MK120 Combo con Teclado y Ratón con Cable para Windows.",
    "image_url": "Imagenes/45.png",
    "caption": "The image depicts a black computer keyboard and mouse set displayed against a clean, white background. The keyboard is positioned diagonally, spanning from the top left to the bottom right of the image, while the mouse is placed beneath the keyboard, slightly offset. Both peripherals are wired, with their wires extending visibly. The keyboard features black keys with white lettering, while the mouse is also black, complementing the keyboard's design. The background is clean and uncluttered, emphasizing the minimalist presentation of the computer peripherals."
  },
  {
    "id": "25",
    "title": "ADATA MEMORIA USB C008 64GB USB 2.0 BLANCO - AZUL.",
    "description": "ADATA LAPIZ USB C008 64GB USB 2.0 BLANCO - AZUL.",
    "image_url": "Imagenes/46.png",
    "caption": "The image displays an ADATA C008 USB 2.0 pen drive with a streamlined design and a two-tone color scheme of white and blue. The blue section appears to be a movable button or panel integrated into the white body, contributing to the device's functionality. The body of the pen drive likely contains printed text in black, such as the brand name \"ADATA\" and model number \"C008,\" although the text details are not fully readable. The USB interface is visible but not emphasized in the overall composition. The device is centrally placed against a plain white background, ensuring it remains the focal point of the image."
  },
  {
    "id": "31",
    "title": "GEMBIRD CONECTOR RJ45 CAT.6 FTP (100 UDS).",
    "description": "GEMBIRD CONECTOR RJ45 CAT.6 FTP (100 UDS).",
    "image_url": "Imagenes/47.png",
    "caption": "The image shows a close-up view of an RJ45 Ethernet connector. The connector features gold-colored interior pins housed within a transparent or white plastic casing. The background is plain white, highlighting the connector's details. The design is consistent with connectors used for high-performance Ethernet cables such as CAT6 or CAT6A cables."
  },
  {
    "id": "88",
    "title": "Maxell CA-MOWR-MXG Gaming M",
    "description": "Maxell CA-MOWR-MXG Gaming M",
    "image_url": "Imagenes/48.png",
    "caption": "The image shows a black and red Maxell wired gaming mouse positioned in the foreground. The mouse features a sleek design with red lighting effects, primarily emanating from the buttons and/or the bottom section. A white \"M\" logo is visible on the surface of the mouse. \n\nBehind the mouse, there is its retail packaging box, standing upright. The box has a bold red and black color scheme and prominently displays the words \"MXG GAMING MOUSE,\" along with an illustration of a warrior or battle-themed imagery, which ties into the gaming aesthetic. The overall design of the mouse and its packaging creates a coordinated and dynamic visual presentation, appealing to gaming enthusiasts."
  },
  {
    "id": "169",
    "title": "Mouse óptico USB",
    "description": "Mouse óptico USB compacto y ergonómico, con sensibilidad precisa. ",
    "image_url": "Imagenes/49.png",
    "caption": "The image displays a wired black computer mouse placed on a plain white surface. The mouse features two buttons and a scroll wheel positioned between them. The body of the mouse appears to be smooth and predominantly black in color, and the wire is visible extending from it. The overall setting is simple and minimalistic, with the plain white background emphasizing the mouse as the focal point."
  },
   {
    "id": "179",
    "title": "Teclado estándar Maxell KB-90",
    "description": "Teclado estándar Maxell KB-90, diseño ergonómico y teclas de respuesta rápida.",
    "image_url": "Imagenes/50.png",
    "caption": "The image displays a black wired keyboard placed on a white background. The keyboard has a simple, minimalistic design with its cable visibly attached, emphasizing elegance and functionality. Its black keycaps and overall design make it visually clean and straightforward, with no additional visible details or text."
  },
  {
    "id": "181",
    "title": "AUDIFONO ONE MOBILE BLUETOOTH",
    "description": "Audífono Bluetooth One Mobile — auricular inalámbrico",
    "image_url": "Imagenes/51.png",
    "caption": "The image shows a pair of black wireless earbuds housed in an open black charging case. The earbuds have a spherical design and are neatly fitted in their designated slots within the case. The set is placed against a clean white background, highlighting its sleek and modern appearance. The image does not include text or additional objects."
  },
  {
    "id": "182",
    "title": "Maxell FUS-9 Audífonos Fusion+ Fury",
    "description": "Audífonos Fusion+ Fury de Maxell FUS-9 — diseño over-ear/cuero",
    "image_url": "Imagenes/52.png",
    "caption": "The image shows a pair of red and black Maxell Fusion+ noise isolation earphones featuring a built-in microphone. The earphones are displayed next to their packaging, which has a black, red, and gray color scheme. The brand name \"Maxell\" is prominently printed on the box in bold lettering near the top, with additional product details below. The packaging design includes a cut-out or display window near the top, showcasing the earphones plugged into a device. The earphones have black and red cables, red and black earbud caps, and a 3.5mm plug at the end, which connects to the cable. The overall design highlights practicality and functionality, with a simple and minimalist aesthetic."
  },
  {
    "id": "190",
    "title": "Maxell Audífonos de Niños",
    "description": "Maxell Audífonos de Niños, diseño compacto y colorido, ajuste cómodo.",
    "image_url": "Imagenes/53.png",
    "caption": "The image displays the packaging for Maxell Kid'z Wireless Headphones, designed for children. The headphones are red and blue with a U-shaped connecting band. The packaging is predominantly white and features a young blond boy wearing the headphones. The boy is depicted holding a glowing blue mobile phone. The design of the box has a playful theme, including a depiction of a blue sky with white clouds in the lower right corner. The brand name \"Maxell\" is displayed at the top of the box, and the product name \"Kid'z Wireless Headphones\" appears prominently. The packaging indicates the product is suitable for children aged 8 and older and includes a \"Wireless Bluetooth\" logo."
  },
  {
    "id": "193",
    "title": "Maxell KIDz Small Size Audífonos Plegables Morado",
    "description": "Audífonos plegables para niños de tamaño reducido, en color morado.",
    "image_url": "Imagenes/54.png",
    "caption": "The image features a pair of wireless headphones with a colorful design that predominantly combines purple and yellow. The earpads are purple, while the headband is yellow. The headphones are foldable and have an adjustable headband, making them portable and suitable for children. The lightweight build and vibrant colors emphasize a playful aesthetic targeted toward a younger audience. The headphones are shown to include a microphone, adding to their functionality."
  },
  {
    "id": "196",
    "title": "SMI EM2180W Monitor 21,45'' FullHD 1",
    "description": "Monitor SMI EM2180W de 21,45 pulgadas con resolución Full HD (1920x1080).",
    "image_url": "Imagenes/55.png",
    "caption": "The image shows a computer monitor placed on a black stand against a plain white background. The monitor is turned on and displays a serene natural landscape featuring tall, snow-capped mountains under a vibrant sky. The scene on the screen evokes a calm and peaceful atmosphere, with a focus on the beauty of nature. The warm tones of the sky, possibly from a sunrise or sunset, harmonize with the stark white of the mountain peaks, creating an overall balanced and tranquil composition."
  },
  {
    "id": "199",
    "title": "SMI EM247CW Monitor 24\" FullHD",
    "description": "Monitor SMI EM247CW de 24 pulgadas con resolución Full HD (1920x1080).",
    "image_url": "Imagenes/56.png",
    "caption": "The image depicts a computer monitor with a black plastic frame and stand, positioned against a plain white background. The monitor screen is turned on and prominently displays a vibrant coastal landscape. The scene shows a sandy beach surrounded by tall white cliffs on both sides, with a deep blue ocean stretching out to the horizon. The sky above is clear and blue, enhancing the peaceful and scenic atmosphere of the display. The cliffs are prominent features, framing the scene like natural borders, while the sandy beach appears to be a central focal point. The monitor design appears sleek and modern with clean lines. There is no visible text or unique branding discernible on the monitor or screen."
  },
  {
    "id": "200",
    "title": "SMI EM27V1W Monitor 27\" FullHD",
    "description": "Monitor SMI EM27V1W de 27 pulgadas con resolución Full HD (1920x1080).",
    "image_url": "Imagenes/57.png",
    "caption": "The image shows a computer monitor with a black border, displaying a blue flower on a white background. The flower appears intricate and is oriented in a way that suggests a 3D or artistic, curled-paper design. The monitor is placed on a black stand, and the surrounding background of the image is pure white."
  },
  {
    "id": "202",
    "title": "SMI EM27M6W Monitor 27\" Curvo Salida de Audio",
    "description": "SMI EM27M6W Monitor  27\" Curvo FullHD 1920x1080 @165 Hz , 2xHDMI",
    "image_url": "Imagenes/58.png",
    "caption": "The image features a curved, wide-screen monitor with a narrow black frame displayed against a plain, white background. The screen shows a serene and picturesque landscape of a mountain range at sunset, with vibrant hues of orange, pink, yellow, and purple filling the sky. A silhouette of a person is seen standing on one of the mountains, gazing at the sunset. The monitor is supported on a stand, though specific details about the stand's design are not highly visible. Overall, the scene conveys a sense of calmness and relaxation."
  },
  {
    "id": "205",
    "title": "SMI EM32M0W Monitor 32\" GAMING, Salida de Audio",
    "description": "SMI EM32M0W Monitor 32\" GAMING CURVO FullHD , DP, Salida de Audio, Bocinas",
    "image_url": "Imagenes/59.png",
    "caption": "The image shows a widescreen monitor with a thin stand placed on a white background. The monitor's display is mostly black with prominently featured yellow and white text, including \"Rapid VA,\" \"180Hz,\" and \"2560 x 1440,\" which indicate the monitor's specifications. There is a small \"Readers' Choice\" logo located in the bottom left corner. The overall presentation suggests that the monitor is a gaming-focused product, highlighting features like high refresh rate and 2K resolution."
  },
  {
    "id": "18",
    "title": "DISCO DURO SEAGATE BARRACUDA HDD",
    "description": "SEAGATE BARRACUDA. Tamaño del HDD: 3.5\", Capacidad del HDD: 1000 GB.",
    "image_url": "Imagenes/60.png",
    "caption": "The image displays a Seagate BarraCuda 3.5-inch internal desktop hard drive alongside its product box. The hard drive has a capacity of 1TB and features a design consistent with Seagate's branding. The box, positioned to the left of the hard drive, prominently displays the \"BarraCuda\" name and a green bird-inspired design. The overall color scheme of the box includes green, black, and white accents, while the hard drive itself predominantly appears in black with silver elements. The objects are set against a plain white background, emphasizing the product details."
  },
  {
    "id": "295",
    "title": "CPU INTEL PENTIUM GOLD G6400",
    "description": "Procesador Intel Pentium Gold G6400, 2 núcleos, 4 hilos, frecuencia base de 4.0 GHz..",
    "image_url": "Imagenes/61.png",
    "caption": "The image shows the blue packaging box of an Intel Pentium Gold Processor. The white text on the box prominently reads \"Intel Pentium Gold Processor,\" with \"Intel\" written twice. The blue box has a simple and sleek design, consistent with Intel's branding. Though the specific model number \"G5420\" is mentioned in one caption, there is insufficient consensus to include it in the description with confidence. The box appears unopened and neatly arranged."
  },
  {
    "id": "299",
    "title": "SP MEMORIA DDR4-3200,CL22,UDIMM,8GB",
    "description": "Memoria RAM SP DDR4-3200, CL22, UDIMM, 8GB",
    "image_url": "Imagenes/62.png",
    "caption": "The image shows a single RAM module placed flat on a white surface. The module has a green circuit board with black memory chips organized into two rows, with eight chips in each row. The orientation of the module places the chips facing upwards, and the connector side with golden pins is visible at the bottom edge. The presentation is straightforward, clearly highlighting the details of the RAM module without additional distractions."
  },
  {
    "id": "297",
    "title": "Gigabyte Placa Base H510M H V2 mATX 1200",
    "description": "Gigabyte Placa Base H510M H V2 mATX 1200",
    "image_url": "Imagenes/63.png",
    "caption": "The image features a black motherboard identified as the Gigabyte H510M H V2. The motherboard is displayed next to its product packaging, which prominently displays the brand name \"Gigabyte\" and the model name \"H510M H V2.\" Both the motherboard and the box are positioned on a solid white background."
  },
  {
    "id": "301",
    "title": "Tooq Fuente Alim. Bitensión TQEP-500S-INT 500W",
    "description": "Tooq Fuente de Alimentación Bitensión TQEP-500S-INT 500W",
    "image_url": "Imagenes/64.png",
    "caption": "The image shows a rectangular box for a power supply unit designed for ATX desktop systems, set against a white background. The product is branded as TooQ ECOPOWER II, with the model name displayed prominently on the box. The packaging features a black design with accents of green, yellow, and white. A fan turbine or cooling design is depicted on the front, emphasizing its technical features. The power output is prominently listed as 500W, alongside a yellow label indicating a 5-year warranty. The overall appearance of the packaging conveys a sense of reliability and efficiency, suitable for high-demand computer setups."
  },
  {
    "id": "305",
    "title": "ROUTER TP-LINK TL-WR841N 300Mbps WIRELESS",
    "description": "Router inalámbrico N a 300 Mbps marca TP-LINK, modelo TL-WR841N.",
    "image_url": "Imagenes/65.png",
    "caption": "The image displays a white wireless router by TP-LINK with two external antennas positioned on top. The router is placed on a plain white background, and its design is simple and functional. No visible text or additional markings are present on the device in the image."
  },
  {
    "id": "307",
    "title": "Sistema Solar Hibrido 3KW",
    "description": "Kit solar 3kW: 3 paneles bifaciales de 610 W.",
    "image_url": "Imagenes/66.png",
    "caption": "The image displays an off-grid solar power system kit neatly arranged on a white background. It features a large solar panel at the center, characterized by a black frame and black solar cells with a white backplane. To the right of the panel is a small inverter with a white casing, a blue display, and several buttons. A battery, marked with \"12V 200Ah,\" is also present, along with associated cables. The components are well-organized, highlighting the system's functionality for off-grid solar energy solutions. In the upper right corner, there is a green text that reads \"off grid,\" reinforcing the theme of the image. The overall presentation emphasizes the neatness and completeness of the solar power system."
  }
]

