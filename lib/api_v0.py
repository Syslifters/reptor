import requests
from posixpath import join as urljoin
import contextlib
import logging
from http.client import responses
from utils.conf import config
from datetime import datetime

log = logging.getLogger('reptor')
# TODO refactor this file 🤷

class LockedException(Exception):
    pass


paths = dict()
paths['private_base'] = "api/v1/pentestusers/self/"
paths['private_notes_base'] = urljoin(paths['private_base'], 'notes/')

paths['project_base'] = f"api/v1/pentestprojects/{config.get('project_id')}/" \
    if config.get('project_id') else None
paths['project_notes_base'] = urljoin(paths['project_base'], 'notes/') \
    if paths['project_base'] else None


endpoints = dict()
for k, v in paths.items():
    try:
        # Note: On first start, without this check config['server] throws keyerror
        if "server" in config:
            endpoints[k] = urljoin(config['server'], v)
    except TypeError:
        endpoints[k] = None


@contextlib.contextmanager
def _lock_note(endpoint):
    r = requests.post(
        urljoin(endpoint, "lock/"),
        headers={'Referer': endpoint,
                 'Content-Type': 'application/json'},
        cookies={'sessionid': config['token']})
    if r.status_code == 200 or r.status_code == 403:
        if r.status_code == 200 and config['cli'].get('force_unlock'):
            r = requests.post(
                urljoin(endpoint, "unlock/"),
                headers={'Referer': endpoint},
                cookies={'sessionid': config['token']})
            try:
                r.raise_for_status()
            except Exception as e:
                raise Exception("Failed to force unlock.") from e
        else:
            if config.get('force_unlock'):
                raise LockedException(
                    'Cannot force unlock. Locked by other user.')
            raise LockedException(
                "The section you want to write to is locked. (Unlock or force: --force-unlock)")
    r.raise_for_status()

    yield
    requests.post(
        urljoin(endpoint, "unlock/"),
        headers={'Referer': endpoint,
                 'Content-Type': 'application/json'},
        cookies={'sessionid': config['token']})


def create_note(title="CLI Note", private_note=False, parent_id=None, order=None, icon=None):
    if private_note:
        endpoint = endpoints['private_notes_base']
    else:
        endpoint = endpoints['project_notes_base']

    r = requests.post(
        endpoint,
        headers={'Referer': endpoint,
                 'Content-Type': 'application/json'},
        cookies={'sessionid': config['token']},
        json={
            "order": order,
            "parent": parent_id,
            "title": title,
        }
    )
    r.raise_for_status()
    note = r.json()
    if icon:
        set_note_icon(urljoin(endpoint, f"{note.get('id')}/"), icon)
    return note


def set_note_icon(endpoint, icon):
    requests.put(
        endpoint,
        headers={'Referer': endpoint,
                 'Content-Type': 'application/json'},
        cookies={'sessionid': config['token']},
        json={
            "icon_emoji": icon
        }
    )


def _get_notes_list(private_note=False):
    if private_note:
        endpoint = endpoints['private_notes_base']
    else:
        endpoint = endpoints['project_notes_base']

    r = requests.get(
        endpoint,
        cookies={'sessionid': config['token'], })
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        try:
            detail = r.json()['detail']
        except Exception:
            detail = None
        raise Exception(
            f'{r.status_code} {responses[r.status_code]}{f" {chr(34)}{detail}{chr(34)}" if detail else ""}') from e
    return r.json()


def _get_note_by_title(title, parent_notename=None, icon=None):
    private_note = False
    if config['cli'].get('private_note'):
        private_note = True
    parent_id = None
    if parent_notename:
        note, _ = _get_note_by_title(parent_notename)
        parent_id = note.get('id')
    notes_list = _get_notes_list(private_note=private_note)

    for note in reversed(notes_list):
        if note.get('title') == title and note.get('parent') == parent_id:
            break
    else:
        # Note does not exist. Create.
        note = create_note(title,
                           parent_id=parent_id,
                           private_note=private_note,
                           icon=icon)
    if private_note:
        return note, urljoin(endpoints['private_notes_base'], note.get('id'))
    else:
        return note, urljoin(endpoints['project_notes_base'], note.get('id'))


def write_note(notename, content, parent_notename=None, force_unlock=False, icon=None):
    _, note_endpoint = _get_note_by_title(
        notename, parent_notename=parent_notename, icon=icon)
    with _lock_note(note_endpoint) if not force_unlock and not config['cli'].get('force_unlock') else contextlib.nullcontext():
        r = requests.get(note_endpoint,
                         headers={'Referer': note_endpoint,
                                  'Content-Type': 'application/json'},
                         cookies={'sessionid': config['token']})
        r.raise_for_status()
        note_info = r.json()
        note_info['text'] += "\n\n"
        if not config['cli'].get('no_timestamp'):
            note_info['text'] += f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
            if "\n" in content:
                if not content.startswith("\n"):
                    note_info['text'] += "\n"
            else:
                note_info['text'] += ": "

        note_info['text'] += content
        r = requests.put(
            note_endpoint,
            headers={'Referer': note_endpoint,
                     'Content-Type': 'application/json'},
            cookies={'sessionid': config['token']},
            json={"text": note_info['text']})
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f'{str(e)} Are you uploading binary content to note? (Try "file" subcommand)') from e
    log.info(f"Note written to \"{notename or 'Uploads'}\".")


def upload_file(filename, notename, content, parent_notename=None, caption=None):
    # Lock during upload to prevent unnecessary uploads and for endpoint setup
    _, note_endpoint = _get_note_by_title(
        notename, parent_notename=parent_notename)
    private_note = False
    if config['cli'].get('private_note'):
        private_note = True
    with _lock_note(note_endpoint) if not config['cli'].get('force_unlock') else contextlib.nullcontext():
        if private_note:
            upload_endpoint = urljoin(
                note_endpoint.rsplit("/", 1)[0], "upload/")
            raise TypeError(
                "Uploading files to private notes is currently not supported")  # TODO fix this as soon as new sysreptor version deployed
        else:
            upload_endpoint = urljoin(
                note_endpoint.rsplit("/", 2)[0], "upload/")
        files = {'file': (filename, content)}  # TODO this might be streamed
        r = requests.post(upload_endpoint,
                          headers={'Referer': note_endpoint},
                          cookies={'sessionid': config['token']},
                          files=files)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            try:
                detail = r.json()['file']
            except Exception:
                detail = None
            raise Exception(
                f'{r.status_code} {responses[r.status_code]}{f" {chr(34)}{detail}{chr(34)}" if detail else ""}') from e
        r = r.json()
        is_image = True if r.get('resource_type') == 'image' else False
        if is_image:
            file_path = f"/images/name/{r['name']}"
            note_content = f"\n![{caption or filename}]({file_path})"
        else:
            file_path = f"/files/name/{r['name']}"
            note_content = f"\n[{caption or filename}]({file_path})"
        write_note(notename, note_content, parent_notename=parent_notename, force_unlock=True)
