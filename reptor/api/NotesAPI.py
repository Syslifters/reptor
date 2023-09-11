import contextlib
import typing
from datetime import datetime
from os.path import basename
from posixpath import join as urljoin

from requests import HTTPError

from reptor.api.APIClient import APIClient
from reptor.lib.errors import MissingArgumentError
from reptor.lib.exceptions import LockedException
from reptor.models.Note import Note
from reptor.utils.file_operations import guess_filetype


class NotesAPI(APIClient):
    """Interacts with Notes Endpoints

    Args:
        APIClient (_type_): _description_
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(require_project_id=False, **kwargs)

        if self.personal_note:
            self.base_endpoint = urljoin(
                self.reptor.get_config().get_server(),
                f"api/v1/pentestusers/self/notes/",
            )
        elif self.project_id:
            self.base_endpoint = urljoin(
                self.reptor.get_config().get_server(),
                f"api/v1/pentestprojects/{self.project_id}/notes/",
            )
        else:
            raise MissingArgumentError(
                "Either specify a project ID (-p|--project_id) or use --personal-note"
            )

    @property
    def personal_note(self):
        return self.reptor.get_config().get_cli_overwrite().get("personal_note")

    def get_notes(self) -> typing.List[Note]:
        """Gets list of notes"""
        self.debug("Getting Notes List")
        response = self.get(self.base_endpoint)
        notes = list()
        for note_data in response.json():
            notes.append(Note(note_data))
        return notes

    def create_note(
        self,
        title="CLI Note",
        parent_id: typing.Optional[str] = None,
        order=None,
        checked=None,
        icon=None,
    ) -> Note:
        self.debug("Creating Note")
        note = self.post(
            self.base_endpoint,
            {
                "order": order,
                "parent": parent_id or None,
                "checked": checked,
                "title": title,
            },
        ).json()
        self.debug(f"We created note with {note}")
        if icon:
            self.set_icon(note.get("id"), icon)
        return Note(note)

    def set_icon(self, notes_id: str, icon: str):
        url = urljoin(self.base_endpoint, f"{notes_id}/")
        self.put(url, {"icon_emoji": icon})

    def write_note(
        self,
        content: str,
        notename: str = "Uploads",
        parent_notename: typing.Optional[str] = None,
        icon: typing.Optional[str] = None,
        no_timestamp: bool = False,
        force_unlock: bool = False,
    ):
        note = self.get_note_by_title(
            notename, parent_notename=parent_notename, icon=icon
        )
        self.debug(f"Working with note: {note.id}")

        with self._lock_note(note.id, force_unlock=force_unlock):
            note_text = note.text + "\n\n"
            if not no_timestamp:
                note_text += f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
                if "\n" in content:
                    if not content.startswith("\n"):
                        note_text += "\n"
                else:
                    note_text += ": "

            note_text += content
            self.debug(f"We are sending data with a lenght of: {len(note_text)}")
            url = urljoin(self.base_endpoint, note.id, "")
            r = self.put(url, {"text": note_text})

            try:
                r.raise_for_status()
                self.info(f'Note written to "{notename}".')
            except HTTPError as e:
                raise HTTPError(
                    f'{str(e)} Are you uploading binary content to note? (Try "file" subcommand)'
                ) from e

    def get_note_by_title(self, title, parent_notename=None, icon=None) -> Note:
        parent_id = None
        if parent_notename:
            note = self.get_note_by_title(parent_notename, icon=icon)
            parent_id = note.id
        notes_list = self.get_notes()

        for note in reversed(notes_list):
            if note.title == title and note.parent == parent_id:
                break
        else:
            # Note does not exist. Create.
            if title == "Uploads":
                icon = "📤"
            note = self.create_note(title=title, parent_id=parent_id, icon=icon)

        return note

    def upload_file(
        self,
        file: typing.Optional[typing.IO] = None,
        content: typing.Optional[bytes] = None,
        notename: typing.Optional[str] = None,
        filename: typing.Optional[str] = None,
        caption: typing.Optional[str] = None,
        parent_notename: typing.Optional[str] = None,
        icon: typing.Optional[str] = None,
        no_timestamp: bool = False,
        force_unlock: bool = False,
    ):
        assert file or content
        assert not (file and content)
        if notename is None:
            notename = "Uploads"

        if file:
            if file.name == "<stdin>":
                self.display("Reading from stdin...")
            elif not filename:
                filename = basename(file.name)
            # TODO this might be streamed to not load entire file to memory
            try:
                content = file.buffer.read()  # type: ignore
            except AttributeError:
                content = file.read()
            if not filename:
                filetype = guess_filetype(content) or "dat"
                filename = f"data.{filetype}"

            if not content:
                self.warning(f"{file.name} is empty. Will not upload.")
                return

        # Lock during upload to prevent unnecessary uploads and for endpoint setup
        note = self.get_note_by_title(notename, parent_notename=parent_notename)
        if self.personal_note:
            url = urljoin(self.base_endpoint, "upload/")
        else:
            url = urljoin(self.base_endpoint.rsplit("/", 2)[0], "upload/")
        with self._lock_note(note.id, force_unlock=force_unlock):
            response_json = self.post(
                url, files={"file": (filename, content)}, json_content=False
            ).json()
            is_image = True if response_json.get("resource_type") == "image" else False
            if is_image:
                file_path = f"/images/name/{response_json['name']}"
                note_content = f"\n![{caption or filename}]({file_path})"
            else:
                file_path = f"/files/name/{response_json['name']}"
                note_content = f"\n[{caption or filename}]({file_path})"

            self.write_note(
                notename=notename,
                content=note_content,
                parent_notename=parent_notename,
                icon=icon,
                no_timestamp=no_timestamp,
                force_unlock=True,
            )

    def _do_lock(self, note_id: str):
        url = urljoin(self.base_endpoint, note_id, "lock/")
        return self.post(url)

    def _do_unlock(self, note_id: str):
        url = urljoin(self.base_endpoint, note_id, "unlock/")
        return self.post(url)

    @contextlib.contextmanager
    def _lock_note(self, note_id: str, force_unlock: bool = False):
        try:
            r = self._do_lock(note_id)
        except HTTPError as e:
            if e.response.status_code == 403:
                locked_by = (
                    e.response.json()
                    .get("lock_info", {})
                    .get("user", {})
                    .get("username")
                )
                if locked_by:
                    raise LockedException(f"Cannot unlock. Locked by @{locked_by}.")
                else:
                    raise LockedException("Cannot unlock. Locked by other user.")
            else:
                raise e
        if not force_unlock and r.status_code == 200:
            raise LockedException(
                "This note is locked. (Unlock or force: --force-unlock)"
            )

        yield

        self._do_unlock(note_id)
