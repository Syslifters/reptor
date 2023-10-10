import contextlib
import typing
from datetime import datetime
from os.path import basename
from posixpath import join as urljoin

from requests import HTTPError

from reptor.api.APIClient import APIClient
from reptor.lib.exceptions import LockedException
from reptor.models.Note import Note
from reptor.utils.file_operations import guess_filetype

from reptor.models.Note import NoteTemplate


class NotesAPI(APIClient):
    """Interacts with Notes Endpoints

    Args:
        APIClient (_type_): _description_
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(require_project_id=False, **kwargs)

        if self.private_note:
            self.base_endpoint = urljoin(
                self.reptor.get_config().get_server(),
                f"api/v1/pentestusers/self/notes/",
            )
        elif self.project_id:
            self.base_endpoint = urljoin(
                self.reptor.get_config().get_server(),
                f"api/v1/pentestprojects/{self.project_id}/notes/",
            )

    @property
    def private_note(self):
        return self.reptor.get_config().get_cli_overwrite().get("private_note")

    def get_notes(self) -> typing.List[Note]:
        """Gets list of notes"""
        self.debug("Getting Notes List")
        response = self.get(self.base_endpoint)
        notes = list()
        for note_data in response.json():
            notes.append(Note(note_data))
        return notes

    def get_note(
        self,
        noteid: typing.Optional[str] = None,
        notetitle: typing.Optional[str] = None,
    ) -> typing.Optional[Note]:
        for note in self.get_notes():
            if noteid:
                if note.id == noteid:
                    return note
            elif notetitle:
                if note.title == notetitle:
                    return note
            else:
                raise ValueError("Either noteid or notetitle must be provided")

    def create_note(
        self,
        title="CLI Note",
        parent_id: typing.Optional[str] = None,
        order=None,
        checked=None,
        icon=None,
    ) -> Note:
        self.debug("Creating Note")
        if title is None:
            raise ValueError("Note title must not be null.")
        note = self.post(
            self.base_endpoint,
            json={
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

    def delete_note(self, notes_id: str):
        url = urljoin(self.base_endpoint, f"{notes_id}/")
        self.delete(url)

    def set_icon(self, notes_id: str, icon: str):
        url = urljoin(self.base_endpoint, f"{notes_id}/")
        self.put(url, json={"icon_emoji": icon})

    def _upload_note(
        self,
        note: Note,
        force_unlock: bool = False,
    ):
        with self._lock_note(note.id, force_unlock=force_unlock):
            self.debug(f"Note has length: {len(note.text)}")
            url = urljoin(self.base_endpoint, note.id, "")
            r = self.put(url, json=note.to_dict())

            try:
                r.raise_for_status()
                self.info(f'Note written to "{note.title}".')
            except HTTPError as e:
                raise HTTPError(
                    f'{str(e)} Are you uploading binary content to note? (Try "file" subcommand)'
                ) from e

    def write_note_templates(
        self,
        note_templates: typing.Union[NoteTemplate, typing.List[NoteTemplate]],
        timestamp: bool = True,
        **kwargs,
    ):
        if not isinstance(note_templates, list):
            note_templates = [note_templates]
        for note_template in note_templates:
            if note_template.parent_notetitle and not note_template.parent:
                note_template.parent = self.get_or_create_note_by_title(
                    note_template.parent_notetitle
                ).id

            note = self.get_note_by_title(
                note_template.title,
                parent_noteid=note_template.parent,
            )
            if note is None:
                new_note = True
                note = self.get_or_create_note_by_title(
                    title=note_template.title,
                    parent_noteid=note_template.parent,
                    parent_notetitle=note_template.parent_notetitle,
                )
            else:
                new_note = False
            self.debug(f"Got note from server {note.title} ({note.id})")

            # Prepare note (append content to existing note, etc)
            note_text = note.text + "\n\n" if note.text else ""
            if (
                timestamp and note_template.text
            ):  # Only add timestamp if there is content
                note_text += f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
                if "\n" in note_template.text:
                    if not note_template.text.startswith("\n"):
                        note_text += "\n"
                else:
                    note_text += ": "
            note_text += note_template.text

            if new_note:
                upload_note = Note.from_note_template(note_template)
                upload_note.parent = note.parent
                upload_note.id = note.id
                upload_note.text = note_text
            else:
                upload_note = note
                upload_note.text = note_text

            # Upload note and children recursively
            self._upload_note(upload_note, **kwargs)
            for child in note_template.children:
                child.parent = note.id
                self.write_note_templates(child, timestamp=timestamp, **kwargs)

    def write_note(
        self,
        timestamp: bool = False,
        force_unlock: bool = False,
        **kwargs,
    ):
        note_template = NoteTemplate.from_kwargs(**kwargs)
        self.write_note_templates(
            note_template, timestamp=timestamp, force_unlock=force_unlock
        )

    def get_note_by_title(
        self,
        title,
        parent_noteid=None,  # Preferred over parent_notetitle
        parent_notetitle=None,
        ignore_parent=False,
    ) -> typing.Optional[Note]:
        if not parent_noteid and parent_notetitle:
            try:
                parent_noteid = self.get_note_by_title(parent_notetitle, ignore_parent=True).id  # type: ignore
            except AttributeError:
                raise ValueError(f'Parent note "{parent_notetitle}" does not exist.')
        notes_list = self.get_notes()

        for note in notes_list:
            if note.title == title and (note.parent == parent_noteid or ignore_parent):
                break
        else:
            return None
        return note

    def get_or_create_note_by_title(
        self,
        title,
        parent_noteid=None,  # Preferred over parent_notetitle
        parent_notetitle=None,
        icon=None,
    ) -> Note:
        if not parent_noteid and parent_notetitle:
            parent_noteid = self.get_or_create_note_by_title(
                parent_notetitle, icon=icon
            ).id
        note = self.get_note_by_title(title, parent_noteid=parent_noteid)
        if not note:
            # Note does not exist. Create.
            if title == "Uploads":
                icon = "📤"
            note = self.create_note(title=title, parent_id=parent_noteid, icon=icon)
        return note

    def upload_file(
        self,
        file: typing.Optional[typing.IO] = None,
        content: typing.Optional[bytes] = None,
        notetitle: typing.Optional[str] = None,
        filename: typing.Optional[str] = None,
        caption: typing.Optional[str] = None,
        parent_notetitle: typing.Optional[str] = None,
        force_unlock: bool = False,
        **kwargs,
    ):
        assert file or content
        assert not (file and content)
        if notetitle is None:
            notetitle = "Uploads"

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
        note = self.get_or_create_note_by_title(
            notetitle, parent_notetitle=parent_notetitle
        )
        if self.private_note:
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
                title=notetitle,
                text=note_content,
                parent_notetitle=parent_notetitle,
                force_unlock=True,
                **kwargs,
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
