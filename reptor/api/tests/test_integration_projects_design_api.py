import os

import pytest

from reptor.lib.reptor import Reptor
from reptor.models.Finding import FindingDataRaw
from reptor.models.Section import SectionDataRaw


@pytest.mark.integration
class TestIntegrationProjectDesignsAPI:
    def test_search(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        all_designs = reptor.api.project_designs.search()
        assert isinstance(all_designs, list)
        assert len(all_designs) > 0
        for design in all_designs:
            assert hasattr(design, "id")
            assert hasattr(design, "name")
        
        search_term = all_designs[0].name
        filtered_designs = reptor.api.project_designs.search(search_term=search_term)
        assert len(filtered_designs) > 0
        assert len(filtered_designs) <= len(all_designs)

    def test_get_project_design(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        all_designs = reptor.api.project_designs.search()
        assert len(all_designs) > 0
        design_id = all_designs[0].id
        design = reptor.api.project_designs.get_project_design(project_design_id=design_id)
        assert hasattr(design, "id")
        assert hasattr(design, "name")
        assert hasattr(design, "finding_fields")
        assert isinstance(design.finding_fields, list)
        assert hasattr(design, "report_fields")
        assert isinstance(design.report_fields, list)

        assert design.id == design_id
    
    @pytest.mark.parametrize(
        "scope",
        ["global", "private"],
    )
    def test_create_and_delete_project_design(self, scope):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        all_designs_before = reptor.api.project_designs.search(scope=scope)

        design_name = "Test Project Design"
        design = reptor.api.project_designs.create_project_design(name=design_name, scope=scope)
        assert hasattr(design, "id")
        assert hasattr(design, "name")
        assert design.name == design_name
        assert design.id not in [d.id for d in all_designs_before]
        assert design.id in [d.id for d in reptor.api.project_designs.search(scope=scope)]

        # Clean up by deleting the created project design
        ret = reptor.api.project_designs.delete_project_design(project_design_id=design.id)
        assert ret is None
        assert design.id not in [d.id for d in reptor.api.project_designs.search(scope=scope)]
    
    def test_update_project_design(self):
        reptor = Reptor(
            server=os.environ.get("SYSREPTOR_SERVER"),
            token=os.environ.get("SYSREPTOR_API_TOKEN"),
        )
        
        # First, create a project design to update
        design_name = "Test Update Project Design"
        design = reptor.api.project_designs.create_project_design(name=design_name, scope="private")
        assert design.id is not None
        
        try:
            # Test updating report_template
            new_template = "<h1>Test Report Template</h1><p>This is a test template.</p>"
            updated_design = reptor.api.project_designs.update_project_design(
                project_design_id=design.id,
                report_template=new_template
            )
            assert hasattr(updated_design, "report_template")
            assert updated_design.report_template == new_template
            
            # Test updating report_styles
            new_styles = "h1 { color: blue; } p { font-size: 14px; }"
            updated_design = reptor.api.project_designs.update_project_design(
                project_design_id=design.id,
                report_styles=new_styles
            )
            assert hasattr(updated_design, "report_styles")
            assert updated_design.report_styles == new_styles
            
            # Test updating both template and styles together
            newer_template = "<h2>Updated Template</h2>"
            newer_styles = "h2 { color: red; }"
            updated_design = reptor.api.project_designs.update_project_design(
                project_design_id=design.id,
                report_template=newer_template,
                report_styles=newer_styles
            )
            assert updated_design.report_template == newer_template
            assert updated_design.report_styles == newer_styles
            
            # Verify the updates persisted by fetching again
            final_design = reptor.api.project_designs.get_project_design(project_design_id=design.id)
            assert final_design.report_template == newer_template
            assert final_design.report_styles == newer_styles
            
            # Test updating preview_findings
            preview_finding_1 = FindingDataRaw()
            preview_finding_1.title = "Test Finding 1"
            preview_finding_1.description = "This is a test finding description #1"
            preview_finding_1.cvss = "CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"
            
            preview_finding_2 = FindingDataRaw()
            preview_finding_2.title = "Test Finding 2"
            preview_finding_2.description = "This is a test finding description #2"
            preview_finding_2.cvss = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"
            
            updated_design = reptor.api.project_designs.update_project_design(
                project_design_id=design.id,
                preview_findings=[preview_finding_1, preview_finding_2]
            )
            assert hasattr(updated_design, "report_preview_data")
            assert isinstance(updated_design.report_preview_data.get("findings"), list)
            assert len(updated_design.report_preview_data.get("findings")) == 2
            assert updated_design.report_preview_data.get("findings")[0].get("title") == preview_finding_1.title
            assert updated_design.report_preview_data.get("findings")[0].get("description") == preview_finding_1.description
            assert updated_design.report_preview_data.get("findings")[0].get("cvss") == preview_finding_1.cvss
            assert updated_design.report_preview_data.get("findings")[1].get("title") == preview_finding_2.title
            assert updated_design.report_preview_data.get("findings")[1].get("description") == preview_finding_2.description
            assert updated_design.report_preview_data.get("findings")[1].get("cvss") == preview_finding_2.cvss
            
            # Test updating preview_report
            preview_report = SectionDataRaw()
            preview_report.executive_summary = "Executive Summary"
            preview_report.scope = "This is the scope"
            
            updated_design = reptor.api.project_designs.update_project_design(
                project_design_id=design.id,
                preview_report=preview_report
            )
            assert hasattr(updated_design, "report_preview_data")
            assert isinstance(updated_design.report_preview_data.get("report"), dict)
            assert updated_design.report_preview_data.get("report").get("executive_summary") == preview_report.executive_summary
            assert updated_design.report_preview_data.get("report").get("scope") == preview_report.scope
            
            # Test updating all parameters together
            final_template = "<div>Complete Test</div>"
            final_styles = "div { margin: 10px; }"
            
            preview_finding_3 = FindingDataRaw()
            preview_finding_3.title = "Combined Test Finding"
            preview_finding_3.severity = "critical"
            
            updated_design = reptor.api.project_designs.update_project_design(
                project_design_id=design.id,
                report_template=final_template,
                report_styles=final_styles,
                preview_findings=[preview_finding_3],
                preview_report=preview_report
            )
            assert updated_design.report_template == final_template
            assert updated_design.report_styles == final_styles
            assert len(updated_design.report_preview_data.get("findings")) == 1
            assert updated_design.report_preview_data.get("findings")[0].get("title") == preview_finding_3.title
            assert updated_design.report_preview_data.get("report").get("executive_summary") == preview_report.executive_summary
            assert updated_design.report_preview_data.get("report").get("scope") == preview_report.scope
            
        finally:
            # Clean up by deleting the created project design
            reptor.api.project_designs.delete_project_design(project_design_id=design.id)
            assert design.id not in [d.id for d in reptor.api.project_designs.search(scope="private")]

