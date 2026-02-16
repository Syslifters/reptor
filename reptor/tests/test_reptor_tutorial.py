import os

import pytest
import requests

import reptor.models as reptor_models
from reptor import Reptor


@pytest.mark.integration
class TestReptorTutorial:
    """
    Test cases for examples from Python Integration Tutorial
    """

    def setup_method(self):
        self.reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )

        self.projects = self.reptor.api.projects.search()
        assert len(self.projects) > 0

    def test_init(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
            project_id=self.projects[0].id,
        )
        project = reptor.api.projects.fetch_project()
        assert isinstance(project, reptor_models.Project.Project)

    def test_project_search(self):
        project_name = self.projects[0].name
        search_term_projects = self.reptor.api.projects.search(search_term=project_name[:5])
        assert len(self.projects) >= len(search_term_projects) > 0

        unfinished_projects = self.reptor.api.projects.search(finished=False)
        finished_projects = self.reptor.api.projects.search(finished=True)
        assert len(unfinished_projects) + len(finished_projects) == len(self.projects)

        assert isinstance(self.projects[0], reptor_models.Project.ProjectOverview)
        assert isinstance(self.projects[0].to_dict(), dict)

    def test_fetch_project(self):
        self.reptor.api.projects.init_project(self.projects[0].id)

        project = self.reptor.api.projects.fetch_project()
        assert isinstance(project, reptor_models.Project.Project)
        assert isinstance(project.to_dict(), dict)
        assert project.name == self.projects[0].name

        html_project = self.reptor.api.projects.fetch_project(html=True)
        assert isinstance(html_project, reptor_models.Project.Project)

    def test_findings(self):
        self.reptor.api.projects.init_project(self.projects[0].id)
        finding_dict = {
            "status": "in-progress",
            "data": {
                "title": "Test Finding",
                "description": "This is a test finding.",
                "affected_components": ["example.com", "example-1.com"],
            },
        }
        my_finding = self.reptor.api.projects.create_finding(finding_dict)
        assert isinstance(my_finding, reptor_models.Finding.FindingRaw)
        assert my_finding.data.title == "Test Finding"
        assert my_finding.data.description == "This is a test finding."
        assert my_finding.data.affected_components == ["example.com", "example-1.com"]
        assert my_finding.status == "in-progress"

        my_finding = self.reptor.api.projects.update_finding(
            my_finding.id,
            {
                "status": "finished",
                "data": {
                    "summary": "My summary",
                }
            }
        )
        assert isinstance(my_finding, reptor_models.Finding.FindingRaw)
        assert my_finding.status == "finished"
        assert my_finding.data.summary == "My summary"

        duplicated_finding = self.reptor.api.projects.create_finding(
            my_finding.to_dict()
        )
        assert isinstance(duplicated_finding, reptor_models.Finding.FindingRaw)
        assert duplicated_finding.data.title == "Test Finding"

        self.reptor.api.projects.delete_finding(duplicated_finding.id)
        with pytest.raises(requests.exceptions.HTTPError):
            # 404 Not Found expected
            self.reptor.api.projects.get_finding(duplicated_finding.id)

    def test_create_finding_from_template(self):
        self.reptor.api.projects.init_project(self.projects[0].id)
        templates = self.reptor.api.templates.search()
        assert len(templates) > 0
        assert isinstance(templates[0], reptor_models.FindingTemplate.FindingTemplate)

        finding = self.reptor.api.projects.create_finding_from_template(
            template_id=templates[0].id,
        )
        assert isinstance(finding, reptor_models.Finding.FindingRaw)
        assert finding.data.title == templates[0].get_main_translation().data.title

        project = self.reptor.api.projects.fetch_project()
        section_id = project.sections[0].id
        
        field = project.sections[0].fields[0]
        section = {
            section_id: {
                field: "Test value",
            }
        }
        my_section = self.reptor.api.projects.update_section(section_id, section)
        assert isinstance(my_section, reptor_models.Section.SectionRaw)

    def test_notes(self):
        self.reptor.api.projects.init_project(self.projects[0].id)
        
        # Test getting project notes
        notes = self.reptor.api.notes.get_notes()
        assert isinstance(notes, list)
        if len(notes) > 0:
            assert hasattr(notes[0], 'title')
            assert hasattr(notes[0], 'id')
            assert hasattr(notes[0], 'parent')
            
            # Test note properties
            first_note = notes[0]
            assert isinstance(first_note.title, str)
            assert hasattr(first_note, 'text')
            assert hasattr(first_note, 'icon_emoji')

        # Find a parent note or create one if none exists
        parent_note = None
        for note in notes:
            if note.parent is None:
                parent_note = note
                break
        
        if parent_note is None:
            # Create a parent note if none exists
            parent_note = self.reptor.api.notes.create_note(
                title="Test Parent Note",
                text="Parent note for testing"
            )
        
        # Test creating a new note with parent
        new_note = self.reptor.api.notes.create_note(
            title="Test Authorization Check",
            parent=parent_note.id,
            checked=False,
            text="Check for authorization issues in the application."
        )
        assert new_note.title == "Test Authorization Check"
        assert new_note.parent == parent_note.id
        assert not new_note.checked
        assert "authorization issues" in new_note.text.lower()

        # Test updating the note
        self.reptor.api.notes.write_note(
            id=new_note.id,
            title="Test Authorization Check (Completed)",
            text="Authorization testing completed successfully.",
            checked=True,
        )
        updated_note = self.reptor.api.notes.get_note(id=new_note.id)
        assert updated_note.title == "Test Authorization Check (Completed)"
        assert updated_note.checked
        assert "completed successfully" in updated_note.text.lower()

        # Test file upload (using a simple text file)
        test_content = b"This is test file content for authorization evidence."
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                self.reptor.api.notes.upload_file(
                    note_id=new_note.id,
                    file=f,
                    filename="test_evidence.txt",
                    caption="Test evidence file for authorization testing."
                )
        finally:
            os.unlink(temp_file_path)
        updated_note = self.reptor.api.notes.get_note(id=new_note.id)
        assert "](/files/name/" in updated_note.text

        # Test note rendering (PDF download)
        pdf_content = self.reptor.api.notes.render(id=new_note.id)
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        # Check if it's a PDF by looking for PDF header
        assert pdf_content.startswith(b'%PDF')

        # Test note duplication
        duplicated_note = self.reptor.api.notes.duplicate(id=new_note.id)
        assert duplicated_note.title == updated_note.title
        assert duplicated_note.id != new_note.id
        assert duplicated_note.parent == new_note.parent

        # Test note deletion (clean up duplicated note)
        self.reptor.api.notes.delete_note(id=duplicated_note.id)
        
        # Verify the duplicated note is deleted by checking it's not in the notes list
        updated_notes = self.reptor.api.notes.get_notes()
        deleted_note_ids = [note.id for note in updated_notes]
        assert duplicated_note.id not in deleted_note_ids

        # Clean up the test note
        self.reptor.api.notes.delete_note(id=new_note.id)
