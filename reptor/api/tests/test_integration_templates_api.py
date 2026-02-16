import os

import pytest

from reptor.lib.reptor import Reptor
from reptor.models.Finding import FindingDataRaw
from reptor.models.FindingTemplate import FindingTemplate, FindingTemplateTranslation


@pytest.mark.integration
class TestIntegrationTemplatesAPI:
    def test_search(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        all_templates = reptor.api.templates.search()
        assert isinstance(all_templates, list)
        if len(all_templates) > 0:
            for template in all_templates:
                assert hasattr(template, "id")
                assert hasattr(template, "translations")
                assert len(template.translations) > 0
            
            # Test search filtering
            search_term = all_templates[0].get_main_title()
            filtered_templates = reptor.api.templates.search(search_term=search_term)
            assert isinstance(filtered_templates, list)
            assert len(filtered_templates) <= len(all_templates)

    def test_get_template(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        
        # First create a template to fetch
        finding_data = FindingDataRaw()
        finding_data.title = "Test Get Template Finding"
        finding_data.description = "This is a test finding for get_template test"
        finding_data.severity = "high"
        finding_data.cvss = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"
        
        translation = FindingTemplateTranslation()
        translation.language = "en-US"
        translation.is_main = True
        translation.data = finding_data
        
        template = FindingTemplate()
        template.translations = [translation]
        template.tags = ["test", "get-template"]
        
        uploaded_template = reptor.api.templates.upload_template(template)
        assert uploaded_template is not None
        assert uploaded_template.id is not None
        
        try:
            # Test fetching the template
            fetched_template = reptor.api.templates.get_template(uploaded_template.id)
            assert hasattr(fetched_template, "id")
            assert hasattr(fetched_template, "translations")
            assert hasattr(fetched_template, "tags")
            assert fetched_template.id == uploaded_template.id
            assert fetched_template.get_main_title() == finding_data.title
            assert fetched_template.get_main_translation().data.description == finding_data.description
            assert set(fetched_template.tags) == set(template.tags)
        finally:
            # Clean up
            reptor.api.templates.delete_template(uploaded_template.id)

    def test_upload_and_delete_template(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        
        all_templates_before = reptor.api.templates.search()
        
        # Create a new template
        finding_data = FindingDataRaw()
        finding_data.title = "Test Upload Finding Template"
        finding_data.description = "This is a test finding template"
        finding_data.severity = "medium"
        finding_data.cvss = "CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N"
        finding_data.recommendation = "Fix the vulnerability"
        
        translation = FindingTemplateTranslation()
        translation.language = "en-US"
        translation.is_main = True
        translation.data = finding_data
        
        template = FindingTemplate()
        template.translations = [translation]
        template.tags = ["test", "upload"]
        
        # Upload the template
        uploaded_template = reptor.api.templates.upload_template(template)
        assert uploaded_template is not None
        assert hasattr(uploaded_template, "id")
        assert uploaded_template.id is not None
        assert uploaded_template.get_main_title() == finding_data.title
        assert uploaded_template.id not in [t.id for t in all_templates_before]
        
        # Verify it exists in search results
        all_templates_after = reptor.api.templates.search()
        assert uploaded_template.id in [t.id for t in all_templates_after]
        
        # Delete the template
        ret = reptor.api.templates.delete_template(uploaded_template.id)
        assert ret is None
        
        # Verify it no longer exists
        all_templates_final = reptor.api.templates.search()
        assert uploaded_template.id not in [t.id for t in all_templates_final]
    
    def test_upload_duplicate_template(self):
        """Test that uploading a template with the same title returns None"""
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        
        # Create a template
        finding_data = FindingDataRaw()
        finding_data.title = "Test Duplicate Template Finding"
        finding_data.description = "This is a test for duplicate detection"
        
        translation = FindingTemplateTranslation()
        translation.language = "en-US"
        translation.is_main = True
        translation.data = finding_data
        
        template = FindingTemplate()
        template.translations = [translation]
        template.tags = ["test", "duplicate"]
        
        # Upload the first template
        uploaded_template = reptor.api.templates.upload_template(template)
        assert uploaded_template is not None
        
        try:
            # Try to upload a template with the same title
            duplicate_template = FindingTemplate()
            duplicate_template.translations = [translation]
            duplicate_template.tags = ["test", "duplicate2"]
            
            result = reptor.api.templates.upload_template(duplicate_template)
            assert result is None  # Should return None for duplicates
        finally:
            # Clean up
            reptor.api.templates.delete_template(uploaded_template.id)
    
    def test_update_template(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        
        # First, create a template to update
        finding_data = FindingDataRaw()
        finding_data.title = "Test Update Template Finding"
        finding_data.description = "Original description"
        finding_data.severity = "low"
        finding_data.cvss = "CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N"
        
        translation = FindingTemplateTranslation()
        translation.language = "en-US"
        translation.is_main = True
        translation.data = finding_data
        
        template = FindingTemplate()
        template.translations = [translation]
        template.tags = ["test", "update"]
        
        uploaded_template = reptor.api.templates.upload_template(template)
        assert uploaded_template is not None
        assert uploaded_template.id is not None
        
        try:
            # Test updating the template
            updated_finding_data = FindingDataRaw()
            updated_finding_data.title = "Updated Template Title"
            updated_finding_data.description = "Updated description with more details"
            updated_finding_data.severity = "critical"
            updated_finding_data.cvss = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
            updated_finding_data.recommendation = "Apply patch immediately"
            
            updated_translation = FindingTemplateTranslation()
            updated_translation.language = "en-US"
            updated_translation.is_main = True
            updated_translation.data = updated_finding_data
            
            updated_template = FindingTemplate()
            updated_template.id = uploaded_template.id
            updated_template.translations = [updated_translation]
            updated_template.tags = ["test", "updated", "critical"]
            
            result = reptor.api.templates.update_template(
                template_id=uploaded_template.id,
                template=updated_template
            )
            
            assert hasattr(result, "id")
            assert result.id == uploaded_template.id
            assert result.get_main_title() == updated_finding_data.title
            assert result.get_main_translation().data.description == updated_finding_data.description
            assert result.get_main_translation().data.severity == updated_finding_data.severity
            assert result.get_main_translation().data.cvss == updated_finding_data.cvss
            assert result.get_main_translation().data.recommendation == updated_finding_data.recommendation
            assert set(result.tags) == set(updated_template.tags)
            
            # Verify the updates persisted by fetching again
            final_template = reptor.api.templates.get_template(uploaded_template.id)
            assert final_template.get_main_title() == updated_finding_data.title
            assert final_template.get_main_translation().data.description == updated_finding_data.description
            assert final_template.get_main_translation().data.severity == updated_finding_data.severity
            assert set(final_template.tags) == set(updated_template.tags)
            
        finally:
            # Clean up by deleting the created template
            reptor.api.templates.delete_template(uploaded_template.id)
            all_templates = reptor.api.templates.search()
            assert uploaded_template.id not in [t.id for t in all_templates]
    
    def test_export(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        
        # First create a template to export
        finding_data = FindingDataRaw()
        finding_data.title = "Test Export Template Finding"
        finding_data.description = "This template will be exported"
        finding_data.severity = "high"
        
        translation = FindingTemplateTranslation()
        translation.language = "en-US"
        translation.is_main = True
        translation.data = finding_data
        
        template = FindingTemplate()
        template.translations = [translation]
        template.tags = ["test", "export"]
        
        uploaded_template = reptor.api.templates.upload_template(template)
        assert uploaded_template is not None
        
        try:
            # Export the template
            exported_data = reptor.api.templates.export(uploaded_template.id)
            assert isinstance(exported_data, bytes)
            assert len(exported_data) > 0
            # Exported data should be a tar.gz archive (check magic bytes)
            # tar.gz files start with 0x1f 0x8b
            assert exported_data[0] == 0x1f
            assert exported_data[1] == 0x8b
        finally:
            # Clean up
            reptor.api.templates.delete_template(uploaded_template.id)
    
    def test_get_templates_by_tag(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        
        # Create templates with specific tags
        tag_to_test = "unique-test-tag-12345"
        
        finding_data_1 = FindingDataRaw()
        finding_data_1.title = "Test Tag Finding 1"
        finding_data_1.description = "First template with unique tag"
        
        translation_1 = FindingTemplateTranslation()
        translation_1.language = "en-US"
        translation_1.is_main = True
        translation_1.data = finding_data_1
        
        template_1 = FindingTemplate()
        template_1.translations = [translation_1]
        template_1.tags = [tag_to_test, "test"]
        
        finding_data_2 = FindingDataRaw()
        finding_data_2.title = "Test Tag Finding 2"
        finding_data_2.description = "Second template with unique tag"
        
        translation_2 = FindingTemplateTranslation()
        translation_2.language = "en-US"
        translation_2.is_main = True
        translation_2.data = finding_data_2
        
        template_2 = FindingTemplate()
        template_2.translations = [translation_2]
        template_2.tags = [tag_to_test, "other"]
        
        # Template without the tag
        finding_data_3 = FindingDataRaw()
        finding_data_3.title = "Test Tag Finding 3"
        finding_data_3.description = "Template without the unique tag"
        
        translation_3 = FindingTemplateTranslation()
        translation_3.language = "en-US"
        translation_3.is_main = True
        translation_3.data = finding_data_3
        
        template_3 = FindingTemplate()
        template_3.translations = [translation_3]
        template_3.tags = ["test", "other"]
        
        uploaded_1 = reptor.api.templates.upload_template(template_1)
        uploaded_2 = reptor.api.templates.upload_template(template_2)
        uploaded_3 = reptor.api.templates.upload_template(template_3)
        
        assert uploaded_1 is not None
        assert uploaded_2 is not None
        assert uploaded_3 is not None
        
        try:
            # Get templates by tag
            tagged_templates = reptor.api.templates.get_templates_by_tag(tag_to_test)
            assert isinstance(tagged_templates, list)
            assert len(tagged_templates) == 2  # Only template_1 and template_2 should be returned
            
            template_ids = [t.id for t in tagged_templates]
            assert uploaded_1.id in template_ids
            assert uploaded_2.id in template_ids
            assert uploaded_3.id not in template_ids
            
            # Verify all returned templates have the tag
            for template in tagged_templates:
                assert tag_to_test in template.tags
        finally:
            # Clean up
            reptor.api.templates.delete_template(uploaded_1.id)
            reptor.api.templates.delete_template(uploaded_2.id)
            reptor.api.templates.delete_template(uploaded_3.id)
