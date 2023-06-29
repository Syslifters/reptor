import lib.api_v0 as api
import sys
from os.path import basename
import logging
from utils.conf import config


log = logging.getLogger('reptor')

def write_note(notename=None, parent=None, content=None, icon=None):
    """
    Notes accept stdin only
    Notes are added as child of 'Uploads' note
    If no notename defined, content gets appended to 'Uploads' note
    """
    if notename is None:
        # No notename given? Take CLI options or default.
        notename = config['cli'].get('notename')
        if notename:
            parent = 'Uploads'
        else:
            notename = 'Uploads'
            icon = "📤"
    if not content:
        log.info("Reading from stdin...")
        content = sys.stdin.read()
    api.write_note(notename, content, parent_notename=parent, icon=icon)


def upload_files(files=None, notename=None, parent=None):
    if notename is None:
        # No notename given? Take CLI options or default.
        notename = config['cli'].get('notename')
        if notename:
            parent = 'Uploads'
        else:
            notename = 'Uploads'
    if files is None:
        files = config['cli'].get('file')
    if not files:
        files = [sys.stdin]

    for file in files:
        if file.name == '<stdin>':
            log.info("Reading from stdin...")
            filename = config['cli'].get('filename')
        else:
            filename = basename(file.name)
        content = file.buffer.read()
        if not filename:
            filetype = _guess_filetype(content) or 'dat'
            filename = f'data.{filetype}'
        
        if not content:
            log.warning(f"{file.name} is empty. Will not upload.")
            continue

        api.upload_file(filename, notename, content, parent_notename=parent, caption=filename)


def _guess_filetype(content):
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
