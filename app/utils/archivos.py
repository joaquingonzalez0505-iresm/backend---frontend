def parece_imagen(contenido: bytes) -> bool:
    """
    Valida mediante bytes de firmas mágicas si el contenido corresponde a una imagen válida (JPG, PNG, WEBP).
    """
    if len(contenido) < 12:
        return False
    # JPEG / JPG (FF D8 FF)
    if contenido.startswith(b"\xff\xd8\xff"):
        return True
    # PNG (\x89 PNG \r \n \x1a \n)
    if contenido.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    # WEBP (RIFF .... WEBP)
    if contenido.startswith(b"RIFF") and contenido[8:12] == b"WEBP":
        return True
    return False
