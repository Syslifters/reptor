def guess_filetype(content):
    ext = None
    if b"PNG" in content[:4]:
        ext = "png"
    elif b"JFIF" in content[:20]:
        ext = "jpg"
    elif b"GIF" in content[:3]:
        ext = "gif"
    elif b"SVG" in content[:4].upper():
        ext = "svg"
    return ext
