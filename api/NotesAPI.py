import contextlib
import logging
import sys
import typing

from datetime import datetime
from os.path import basename
from posixpath import join as urljoin

from requests import HTTPError

from api.APIClient import APIClient
from api.errors import LockedException
from api.models import Note
from utils.file_operations import guess_filetype

from core.logger import reptor_logger


class NotesAPI(APIClient):
    """Interacts with Notes Endpoints

    Args:
        APIClient (_type_): _description_
    """

    def __init__(self, reptor) -> None:
        super().__init__(reptor)

        if self.private_note:
            self.base_endpoint = urljoin(
                self._config.get_server(), f"api/v1/pentestusers/self/notes/"
            )
        elif self._config.get_project_id():
            self.base_endpoint = urljoin(
                self._config.get_server(),
                f"api/v1/pentestprojects/{self._config.get_project_id()}/notes/",
            )
        else:
            reptor_logger.fail_with_exit(
                "Either specify a project ID (-p|--project_id) or use --private-note"
            )

    @property
    def private_note(self):
        return self._config.get_cli_overwrite().get("private_note")

    def get_notes(self) -> typing.List[Note]:
        """Gets list of notes"""
        response = self.get(self.base_endpoint)
        notes = list()
        for note_data in response.json():
            notes.append(Note(note_data))
        return notes

    def create_note(
        self, title="CLI Note", parent_id=None, order=None, icon=None
    ) -> Note:
        note = self.post(
            self.base_endpoint,
            {
                "order": order,
                "parent": parent_id,
                "title": title,
            },
        ).json()
        if icon:
            self.set_icon(note.get("id"), icon)
        return Note(note)

    def set_icon(self, notes_id: str, icon: str):
        url = urljoin(self.base_endpoint, f"{notes_id}/")
        self.put(url, {"icon_emoji": icon})

    def write_note(
        self,
        notename=None,
        parent_notename=None,
        content=None,
        icon=None,
        no_timestamp=False,
        force_unlock=False,
    ):
        """
        Notes accept stdin only
        Notes are added as child of 'Uploads' note
        If no notename defined, content gets appended to 'Uploads' note
        """
        if not content:
            reptor_logger.info("Reading from stdin...")
            content = sys.stdin.read()

        note = self.get_note_by_title(
            notename, parent_notename=parent_notename, icon=icon
        )

        self.reptor.logger.debug(f"Working with note: {note.id}")

        with self._auto_lock_note(
            note.id
        ) if not force_unlock else contextlib.nullcontext():
            note_text = note.text + "\n\n"
            if not no_timestamp:
                note_text += f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
                if "\n" in content:
                    if not content.startswith("\n"):
                        note_text += "\n"
                else:
                    note_text += ": "

            note_text += content
            self.reptor.logger.debug(
                f"We are sending data with a lenght of: {len(note_text)}"
            )
            url = urljoin(self.base_endpoint, note.id)
            r = self.put(url, {"text": note_text})

            try:
                r.raise_for_status()
            except HTTPError as e:
                raise HTTPError(
                    f'{str(e)} Are you uploading binary content to note? (Try "file" subcommand)'
                ) from e
        reptor_logger.info(f'Note written to "{notename}".')

    def get_note_by_title(self, title, parent_notename=None, icon=None) -> Note:
        parent_id = None
        if parent_notename:
            note = self.get_note_by_title(parent_notename)
            parent_id = note.id
        notes_list = self.get_notes()

        for note in reversed(notes_list):
            if note.title == title and note.parent == parent_id:
                break
        else:
            # Note does not exist. Create.
            note = self.create_note(title=title, parent_id=parent_id, icon=icon)

        return note

    def upload_file(
        self,
        files=None,
        filename=None,
        caption=None,
        notename=None,
        parent_notename=None,
        icon=None,
        no_timestamp=False,
        force_unlock=False,
    ):
        if not files:
            return

        for file in files:
            if file.name == "<stdin>":
                reptor_logger.info("Reading from stdin...")
            else:
                filename = basename(file.name)
            content = file.buffer.read()
            if not filename:
                filetype = guess_filetype(content) or "dat"
                filename = f"data.{filetype}"

            if not content:
                reptor_logger.warning(f"{file.name} is empty. Will not upload.")
                continue

            # Lock during upload to prevent unnecessary uploads and for endpoint setup
            note = self.get_note_by_title(notename, parent_notename=parent_notename)
            if self.private_note:
                url = urljoin(self.base_endpoint, "upload/")
                raise TypeError(
                    "Uploading files to private notes is currently not supported"
                )  # TODO fix this as soon as new sysreptor version deployed
            else:
                url = urljoin(self.base_endpoint.rsplit("/", 2)[0], "upload/")
            with self._auto_lock_note(
                note.id
            ) if not force_unlock else contextlib.nullcontext():
                # TODO this might be streamed
                files = {"file": (filename, content)}
                response_json = self.post(url, files=files, json_content=False).json()
                is_image = (
                    True if response_json.get("resource_type") == "image" else False
                )
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

    def _lock_note(self, note_id):
        url = urljoin(self.base_endpoint, note_id, "lock/")
        return self.post(url)

    def _unlock_note(self, note_id):
        url = urljoin(self.base_endpoint, note_id, "unlock/")
        return self.post(url)

    @contextlib.contextmanager
    def _auto_lock_note(self, note_id):
        r = self._lock_note(note_id)
        if r.status_code == 200 or r.status_code == 403:
            if r.status_code != 200:
                if self.force_unlock:
                    raise LockedException("Cannot force unlock. Locked by other user.")
                else:
                    raise LockedException(
                        "The section you want to write to is locked. "
                        "(Unlock or force: --force-unlock)"
                    )
        r.raise_for_status()

        yield

        self._unlock_note(note_id)
