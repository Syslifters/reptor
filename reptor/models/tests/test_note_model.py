from ..Note import Note, NoteTemplate


class TestNoteModel:
    def test_from_note_template(self):
        note_template = NoteTemplate(
            data={
                "title": "Note Title",
                "text": "Note Text",
                "checked": True,
                "icon_emoji": "📤",
                "status_emoji": "📤",
                "order": 1,
                "parent": "abc-def",
            }
        )
        note = Note.from_note_template(note_template)
        assert note.title == "Note Title"
        assert note.text == "Note Text"
        assert note.checked is True
        assert note.icon_emoji == "📤"
        assert note.status_emoji == "📤"
        assert note.order == 1
        assert note.parent == "abc-def"

    def test_from_kwargs(self):
        note_template = NoteTemplate.from_kwargs(
            title="Note Title",
            text="Note Text",
            checked=True,
            icon_emoji="📤",
            status_emoji="📤",
            order=1,
            parent="abc-def",
        )
        assert note_template.title == "Note Title"
        assert note_template.text == "Note Text"
        assert note_template.checked is True
        assert note_template.icon_emoji == "📤"
        assert note_template.status_emoji == "📤"
        assert note_template.order == 1
        assert note_template.parent == "abc-def"
