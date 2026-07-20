import os
import sys
import tarfile
from pathlib import Path


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


def safe_extractall(tar: tarfile.TarFile, destination: str | os.PathLike) -> None:
    destination = Path(destination).resolve()
    if sys.version_info >= (3, 12):
        tar.extractall(destination, filter="data")
        return

    for member in tar.getmembers():
        if member.name.startswith(("/", os.sep)) or Path(member.name).is_absolute():
            raise tarfile.ExtractError(f"Refusing to extract absolute path: {member.name!r}")

        target_path = (destination / member.name).resolve()
        if not target_path.is_relative_to(destination):
            raise tarfile.ExtractError(f"Refusing to extract unsafe path: {member.name!r}")

        if member.issym() or member.islnk() or member.isdev() or member.isfifo():
            raise tarfile.ExtractError(f"Refusing to extract unsafe member type: {member.name!r}")

        tar.extract(member, path=destination)
