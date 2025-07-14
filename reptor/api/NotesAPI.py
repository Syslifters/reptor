import typing
from datetime import datetime
from os.path import basename
from posixpath import join as urljoin

from requests import HTTPError

from reptor.api.APIClient import APIClient
from reptor.models.Note import Note
from reptor.utils.file_operations import guess_filetype

from reptor.models.Note import NoteTemplate


class NotesAPI(APIClient):
    """API client for interacting with SysReptor project notes or personal notes.

    Example:
        ```python
        from reptor import Reptor

        reptor = Reptor(
            server=os.environ.get("REPTOR_SERVER"),
            token=os.environ.get("REPTOR_TOKEN"),
            personal_notes=False,
        )

        # NotesAPI is available as reptor.api.notes, e.g.:
        reptor.api.notes.get_notes()
        ```
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(require_project_id=False, **kwargs)

        if self.personal_note:
            self.base_endpoint = urljoin(
                self.reptor.get_config().get_server(),
                "api/v1/pentestusers/self/notes/",
            )
        elif self.project_id:
            self.base_endpoint = urljoin(
                self.reptor.get_config().get_server(),
                f"api/v1/pentestprojects/{self.project_id}/notes/",
            )

    @property
    def personal_note(self):
        return self.reptor.get_config().get("personal_note")

    def get_notes(self) -> typing.List[Note]:
        """Gets list of all notes in the current context (project notes or personal notes).

        Returns:
            List of notes for this project or user

        Example:
            ```python
            reptor.api.notes.get_notes()
            ```
        """
        response = self.get(self.base_endpoint)
        notes = list()
        for note_data in response.json():
            notes.append(Note(note_data))
        return notes

    def get_note(
        self,
        id: typing.Optional[str] = None,
        title: typing.Optional[str] = None,
    ) -> typing.Optional[Note]:
        """Gets a single note by ID or title.

        Args:
            id (str, optional): Note ID to retrieve (prioritized over title)
            title (str, optional): Note title to search for

        Returns:
            Note object if found, None otherwise

        Example:
            ```python
            # Get note by ID
            note = reptor.api.notes.get_note(id="983a7e95-b2d9-4d57-984e-08496264cce8")
            
            # Get note by title
            note = reptor.api.notes.get_note(title="My Note")
            ```
        """
        for note in self.get_notes():
            if id:
                if note.id == id:
                    return note
            elif title:
                if note.title == title:
                    return note
            else:
                raise ValueError("Either id or title must be provided")

    def create_note(
        self,
        title="Note by reptor",
        text=None,
        parent: typing.Optional[str] = None,
        order=None,
        checked=None,
        icon=None,
    ) -> Note:
        """Creates a new note.

        Args:
            title (str, optional): Note title. Defaults to "Note by reptor".
            text (str, optional): Note content. Defaults to None.
            parent (str, optional): Parent note ID for nested notes. Defaults to None.
            order (int, optional): Sort order for the note. Defaults to None.
            checked (bool, optional): Checkbox state for checklist notes. Defaults to None.
            icon (str, optional): Emoji icon for the note. Defaults to None.

        Returns:
            Created note object

        Example:
            ```python
            reptor.api.notes.create_note(
                title="My New Note",
                text="This is the content",
                icon="📝"
            )
            ```
        """
        if title is None:
            raise ValueError("Note title must not be null.")
        note = self.post(
            self.base_endpoint,
            json={
                "order": order,
                "parent": parent or None,
                "checked": checked,
                "title": title,
                "text": text or "",
            },
        ).json()
        if icon:
            self.set_icon(note.get("id"), icon)
        elif title == "Uploads":
            self.set_icon(note.get("id"), "📤")
        return Note(note)

    def write_note(
        self,
        timestamp: bool = False,
        **kwargs,
    ):
        """Updates notes, appends text to a note.

        Args:
            id (str, optional): Note ID to update
            title (str, optional): Note title.
            text (str, optional): Append text to the note. Defaults to empty string.
            timestamp (bool, optional): Prepend timestamp to newly inserted text. Defaults to False.
            checked (bool, optional): Checkbox state for checklist notes.
            icon_emoji (str, optional): Emoji icon for the note.
            order (int, optional): Sort order for the note. Defaults to 0.

        Example:
            ```python
            reptor.api.notes.write_note(
                title="Security Finding",
                text="Found vulnerability in authentication",
                timestamp=True
            )
            ```
        """
        note_template = NoteTemplate.from_kwargs(**kwargs)
        self.write_note_templates(
            note_template, timestamp=timestamp
        )

    def write_note_templates(
        self,
        note_templates: typing.Union[NoteTemplate, typing.List[NoteTemplate]],
        timestamp: bool = True,
        **kwargs,
    ):
        if not isinstance(note_templates, list):
            note_templates = [note_templates]
        for note_template in note_templates:
            if note_template.id:
                new_note = False
                note = self.get_note(id=note_template.id)
                if not note:
                    raise ValueError(f'Note with ID "{note_template.id}" does not exist.')
            else:
                if note_template.parent_title and not note_template.parent:
                    note_template.parent = self.get_or_create_note_by_title(
                        note_template.parent_title
                    ).id

                note = None
                if not note_template.force_new:
                    note = self.get_note_by_title(
                        note_template.title,
                        parent=note_template.parent,
                    )
                if note is None:
                    new_note = True
                    note = self.create_note(
                        title=note_template.title,
                        parent=note_template.parent or None,
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
            note_text += note_template.text or ""

            if new_note:
                upload_note = Note.from_note_template(note_template)
                upload_note.parent = note.parent
                upload_note.id = note.id
                upload_note.text = note_text
            else:
                upload_note = note
                if note_template.title:
                    upload_note.title = note_template.title
                if note_template.checked is not None:
                    upload_note.checked = note_template.checked
                if note_template.icon_emoji:
                    upload_note.icon_emoji = note_template.icon_emoji
                if note_template.order:
                    upload_note.order = note_template.order
                upload_note.text = note_text

            # Upload note and children recursively
            self._upload_note(upload_note, **kwargs)
            for child in note_template.children:
                child.parent = note.id
                self.write_note_templates(child, timestamp=timestamp, **kwargs)

    def set_icon(self, id: str, icon: str):
        """Sets an emoji icon for a note.

        Args:
            id (str): Note ID
            icon (str): Emoji character to set as icon

        Example:
            ```python
            reptor.api.notes.set_icon("983a7e95-b2d9-4d57-984e-08496264cce8", "🔒")
            ```
        """
        url = urljoin(self.base_endpoint, f"{id}/")
        self.put(url, json={"icon_emoji": icon})

    def upload_file(
        self,
        file: typing.Optional[typing.IO] = None,
        content: typing.Optional[bytes] = None,
        filename: typing.Optional[str] = None,
        caption: typing.Optional[str] = None,
        note_id: typing.Optional[str] = None,
        note_title: typing.Optional[str] = None,
        parent_title: typing.Optional[str] = None,
        **kwargs,
    ):
        """Uploads a file to a note.

        Args:
            file (typing.IO, optional): File object to upload
            content (bytes, optional): File content as bytes
            filename (str, optional): Name for the uploaded file
            caption (str, optional): Caption for the file link
            note_id (str, optional): ID of note to upload to
            note_title (str, optional): Title of note to upload to
            parent_title (str, optional): Parent note title for organization
            **kwargs: Additional parameters for note writing

        Example:
            ```python
            # Upload from file
            with open("screenshot.png", "rb") as f:
                reptor.api.notes.upload_file(
                    file=f,
                    note_title="Evidence",
                    caption="Login page screenshot"
                )
            
            # Upload from bytes
            reptor.api.notes.upload_file(
                content=b"file content",
                filename="data.txt",
                note_title="Files"
            )
            ```
        """
        assert file or content
        assert not (file and content)

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

        if not note_id:
            note_id = self.get_or_create_note_by_title(
                note_title or "Uploads", parent_title=parent_title
            ).id
        if self.personal_note:
            url = urljoin(self.base_endpoint, "upload/")
        else:
            url = urljoin(self.base_endpoint.rsplit("/", 2)[0], "upload/")
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
            id=note_id,
            text=note_content,
            **kwargs,
        )

    def render(
        self,
        id: str,
    ) -> bytes:
        """Renders a note to PDF format.

        Args:
            id (str): Note ID to render

        Returns:
            PDF content as bytes

        Example:
            ```python
            pdf_data = reptor.api.notes.render("note-uuid-here")
            with open("note.pdf", "wb") as f:
                f.write(pdf_data)
            ```
        """
        url = urljoin(self.base_endpoint, f"{id}/export-pdf/")
        response = self.post(url)
        response.raise_for_status()
        return response.content

    def delete_note(self, id: str):
        """Deletes a note by ID.

        Args:
            id (str): Note ID to delete

        Example:
            ```python
            reptor.api.notes.delete_note("983a7e95-b2d9-4d57-984e-08496264cce8")
            ```
        """
        url = urljoin(self.base_endpoint, f"{id}/")
        self.delete(url)

    def duplicate(
        self,
        id: str,
    ) -> Note:
        """Creates a note duplicate.

        Args:
            id (str): Note ID to duplicate

        Returns:
            Duplicated note object

        Example:
            ```python
            duplicate_note = reptor.api.notes.duplicate("note-uuid-here")
            print(f"Duplicated note: {duplicate_note.title}")
            ```
        """
        url = urljoin(self.base_endpoint, f"{id}/copy/")
        response = self.post(url)
        response.raise_for_status()
        return Note(response.json())

    def get_note_by_title(
        self,
        title,
        parent=None,  # Preferred over parent_title
        parent_title=None,
        any_parent=False,
    ) -> typing.Optional[Note]:
        if not parent and parent_title:
            try:
                parent = self.get_note_by_title(parent_title, any_parent=True).id  # type: ignore
            except AttributeError:
                raise ValueError(f'Parent note "{parent_title}" does not exist.')
        notes_list = self.get_notes()

        for note in notes_list:
            if note.title == title and (note.parent == parent or any_parent):
                break
        else:
            return None
        return note

    def get_or_create_note_by_title(
        self,
        title,
        parent=None,  # Preferred over parent_title
        parent_title=None,
        icon=None,
    ) -> Note:
        if not parent and parent_title:
            parent = self.get_or_create_note_by_title(
                parent_title, icon=icon
            ).id
        note = self.get_note_by_title(title, parent=parent)
        if not note:
            # Note does not exist. Create.
            note = self.create_note(title=title, parent=parent, icon=icon)
        return note

    def _upload_note(
        self,
        note: Note,
    ):
        url = urljoin(self.base_endpoint, note.id, "")
        r = self.put(url, json=note.to_dict())

        try:
            r.raise_for_status()
            self.display(f'Note written to "{note.title}".')
        except HTTPError as e:
            raise HTTPError(
                f'{str(e)} Are you uploading binary content to note? (Try "file" subcommand)'
            ) from e
