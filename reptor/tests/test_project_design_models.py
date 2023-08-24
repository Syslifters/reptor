import json

from reptor.models.ProjectDesign import ProjectDesign, ProjectDesignField


class TestProjectDesignModelParsing:
    example_project_design = """
    {"id":"9ef57060-9bcc-4410-b1fd-744d7657558c","created":"2023-07-14T14:19:06.805883Z","updated":"2023-07-14T15:35:05.162391Z","source":"created","scope":"private","name":"Demo Report v1.12","language":"en-US","details":"https://demo.sysre.pt/api/v1/projecttypes/9ef57060-9bcc-4410-b1fd-744d7657558c","assets":"https://demo.sysre.pt/api/v1/projecttypes/9ef57060-9bcc-4410-b1fd-744d7657558c/assets","copy_of":"da029ad9-ee5b-4f31-820e-a0e48ddbc8b8","lock_info":{"created":"2023-07-14T17:18:19.072853Z","updated":"2023-07-14T17:18:49.380931Z","last_ping":"2023-07-14T17:18:49.380870Z","expires":"2023-07-14T17:20:19.380870Z","user":{"id":"80bcd0a1-4a7d-4288-9853-8592662c8ee3","username":"demo-eoNeCdnO","name":"","title_before":null,"first_name":"","middle_name":null,"last_name":"","title_after":null,"is_active":true}},"report_template":"","report_preview_data":{"report":{"pta":"TODO: screenshots of PTA"},"findings":[{"id":"a10eed1a-07f5-46ef-bf3a-b78208e72272","cvss":"CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H","title":"Demo Finding Critical","summary":"TODO summary","references":["https://example.com"],"description":"TODO description","wstg_category":"IDNT","recommendation":"TODO recommendation","affected_components":["https://example.com"],"recomlist":["quidem aliquam","est possimus"],"new_field1":{"date":"2023-07-14","enum":"enum_val","user":null,"new_cvss":"n/a","new_field2":"sed laudantium","new_field4":"quam similique","nested_field":"Combobox Value"},"importantenum":"enum_val"}]},"report_fields":{"draft":{"type":"boolean","label":"Is Draft?","origin":"custom","default":true},"scope":{"type":"markdown","label":"Scope","origin":"custom","default":"**TODO:","required":true},"title":{"type":"string","label":"Title","origin":"core","default":"TODO report title","required":true,"spellcheck":false},"duration":{"type":"string","label":"Duration","origin":"custom","default":"TODO person days","required":true,"spellcheck":false},"end_date":{"type":"date","label":"Pentest End Date","origin":"custom","default":null,"required":true},"start_date":{"type":"date","label":"Pentest Start Date","origin":"custom","default":null,"required":true},"report_date":{"type":"date","label":"Report Date","origin":"custom","default":null,"required":true},"customer_name":{"type":"string","label":"Customer","origin":"custom","default":"TODO company","required":true,"spellcheck":false},"receiver_name":{"type":"string","label":"Receiver Name","origin":"custom","default":"TODO receiver","required":true,"spellcheck":false},"provided_users":{"type":"markdown","label":"Users and Permissions","origin":"custom","default":"**TODO: Provided Use","required":true},"report_version":{"type":"string","label":"Report Version","origin":"custom","default":"1.0","required":true,"spellcheck":false},"list_of_changes":{"type":"list","items":{"type":"object","label":"","origin":"custom","properties":{"date":{"type":"date","label":"Date","origin":"custom","default":null,"required":true},"version":{"type":"string","label":"Version","origin":"custom","default":"TODO version","required":true,"spellcheck":false},"description":{"type":"string","label":"Description","origin":"custom","default":"TODO description","required":true,"spellcheck":false}}},"label":"List of Changes","origin":"custom","required":true},"customer_address":{"type":"object","label":"Address","origin":"custom","properties":{"city":{"type":"string","label":"City","origin":"custom","default":"TODO city","required":true,"spellcheck":false},"street":{"type":"string","label":"Street","origin":"custom","default":"TODO street","required":true,"spellcheck":false}}},"appendix_sections":{"type":"list","items":{"type":"object","label":"","origin":"custom","properties":{"title":{"type":"string","label":"Title","origin":"custom","default":"TODO appendix title","required":true,"spellcheck":false},"content":{"type":"markdown","label":"Content","origin":"custom","default":"TODO appendix content","required":true}}},"label":"Appendix","origin":"custom","required":true},"executive_summary":{"type":"markdown","label":"Executive Summary","origin":"custom","default":"**TODO:","required":true}},"report_sections":[{"id":"executive_summary","label":"Executive Summary","fields":["executive_summary"]},{"id":"scope","label":"Scope","fields":["scope","start_date","end_date","duration","provided_users"]},{"id":"customer","label":"Customer","fields":["customer_name","customer_address","receiver_name"]},{"id":"other","label":"Other","fields":["title","report_date","report_version","list_of_changes","draft"]},{"id":"appendix","label":"Appendix","fields":["appendix_sections"]}],"finding_fields":{"cvss":{"type":"cvss","label":"CVSS","origin":"core","default":"n/a","required":true},"title":{"type":"string","label":"Titel","origin":"core","default":"TODO finding title","required":true,"spellcheck":false},"summary":{"type":"markdown","label":"Overview","origin":"predefined","default":"TODO summary","required":true},"recomlist":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"recomlist","origin":"custom","required":true},"new_field1":{"type":"object","label":"New Field","origin":"custom","properties":{"date":{"type":"date","label":"New Field","origin":"custom","default":"2023-07-14","required":true},"enum":{"type":"enum","label":"New Field","origin":"custom","choices":[{"label":"Enum Value","value":"enum_val"},{"label":"New Enum Value","value":"new_value1"}],"default":null,"required":true},"user":{"type":"user","label":"New Field","origin":"custom","required":false},"new_cvss":{"type":"cvss","label":"New Field","origin":"custom","default":"n/a","required":true},"new_field2":{"type":"string","label":"New Field","origin":"custom","default":null,"required":true,"spellcheck":false},"new_field4":{"type":"string","label":"New Field","origin":"custom","default":null,"required":true,"spellcheck":false},"nested_field":{"type":"combobox","label":"Nested Field","origin":"custom","default":null,"required":true,"suggestions":["Combobox Value"]}}},"references":{"type":"list","items":{"type":"string","label":"Reference","origin":"predefined","default":"TODO reference","required":true,"spellcheck":false},"label":"References","origin":"predefined","required":false},"description":{"type":"markdown","label":"Details","origin":"predefined","default":"TODO description","required":true},"importantenum":{"type":"enum","label":"importantenum","origin":"custom","choices":[{"label":"Enum Value","value":"enum_val"},{"label":"New Enum Value","value":"new_value1"},{"label":"New Enum Value","value":"new_value1"}],"default":null,"required":true},"recommendation":{"type":"markdown","label":"Recommendation","origin":"predefined","default":"TODO recommendation","required":true},"affected_components":{"type":"list","items":{"type":"string","label":"Component","origin":"predefined","default":"TODO affected component","required":true,"spellcheck":false},"label":"Affected Components","origin":"predefined","required":true}},"finding_field_order":["title","cvss","references","affected_components","summary","description","recommendation","importantenum","recomlist","new_field1"]}"""

    def test_empty_project_design_parsing(self):
        project_design = ProjectDesign()
        assert isinstance(project_design, ProjectDesign)

        # Report Fields
        assert isinstance(project_design.report_fields[0], ProjectDesignField)
        assert project_design.report_fields[0].origin == "core"
        assert project_design.report_fields[0].name == "title"
        assert project_design.report_fields[0].type == "string"

        # Finding Fields
        assert all(
            [
                isinstance(field, ProjectDesignField)
                for field in project_design.finding_fields
            ]
        )
        assert all(
            [
                field.origin == "predefined"
                for field in project_design.finding_fields
                if field.name != "title"
            ]
        )

        assert project_design.finding_fields[0].name == "cvss"
        assert project_design.finding_fields[0].type == "cvss"

        assert project_design.finding_fields[1].name == "title"
        assert project_design.finding_fields[1].type == "string"
        assert project_design.finding_fields[1].origin == "core"

        assert project_design.finding_fields[2].name == "impact"
        assert project_design.finding_fields[2].type == "markdown"

        assert project_design.finding_fields[3].name == "summary"
        assert project_design.finding_fields[3].type == "markdown"

        assert project_design.finding_fields[4].name == "severity"
        assert project_design.finding_fields[4].type == "enum"
        assert [c["value"] for c in project_design.finding_fields[4].choices] == [
            "info",
            "low",
            "medium",
            "high",
            "critical",
        ]

        assert project_design.finding_fields[5].name == "references"
        assert project_design.finding_fields[5].type == "list"
        assert project_design.finding_fields[5].items.type == "string"

        assert project_design.finding_fields[6].name == "description"
        assert project_design.finding_fields[6].type == "markdown"

        assert project_design.finding_fields[7].name == "precondition"
        assert project_design.finding_fields[7].type == "string"

        assert project_design.finding_fields[8].name == "retest_notes"
        assert project_design.finding_fields[8].type == "markdown"

        assert project_design.finding_fields[9].name == "retest_status"
        assert project_design.finding_fields[9].type == "enum"
        assert [c["value"] for c in project_design.finding_fields[9].choices] == [
            "open",
            "resolved",
            "partial",
            "changed",
            "accepted",
            "new",
        ]

        assert project_design.finding_fields[10].name == "wstg_category"
        assert project_design.finding_fields[10].type == "enum"
        assert [c["value"] for c in project_design.finding_fields[10].choices] == [
            "INFO",
            "CONF",
            "IDNT",
            "ATHN",
            "ATHZ",
            "SESS",
            "INPV",
            "ERRH",
            "CRYP",
            "BUSL",
            "CLNT",
            "APIT",
        ]

        assert project_design.finding_fields[11].name == "recommendation"
        assert project_design.finding_fields[11].type == "markdown"

        assert project_design.finding_fields[12].name == "owasp_top10_2021"
        assert project_design.finding_fields[12].type == "enum"
        assert [c["value"] for c in project_design.finding_fields[12].choices] == [
            "A01_2021",
            "A02_2021",
            "A03_2021",
            "A04_2021",
            "A05_2021",
            "A06_2021",
            "A07_2021",
            "A08_2021",
            "A09_2021",
            "A10_2021",
        ]

        assert project_design.finding_fields[13].name == "affected_components"
        assert project_design.finding_fields[13].type == "list"
        assert project_design.finding_fields[13].items.type == "string"

        assert project_design.finding_fields[14].name == "short_recommendation"
        assert project_design.finding_fields[14].type == "string"

    def test_project_design_parsing(self):
        api_test_data = json.loads(self.example_project_design)
        project_design = ProjectDesign(api_test_data)
        assert project_design.id == "9ef57060-9bcc-4410-b1fd-744d7657558c"
        assert project_design.source == "created"
        assert project_design.scope == "private"
        assert project_design.name == "Demo Report v1.12"
        assert project_design.language == "en-US"
        assert isinstance(project_design.finding_fields, list)
        assert isinstance(project_design.report_fields, list)
        assert len(project_design.finding_fields) == 10
        assert len(project_design.report_fields) == 15

        report_field_names = [field.name for field in project_design.report_fields]
        assert all(
            [
                name in report_field_names
                for name in [
                    "draft",
                    "scope",
                    "title",
                    "duration",
                    "end_date",
                    "start_date",
                    "report_date",
                    "customer_name",
                    "receiver_name",
                    "provided_users",
                    "report_version",
                    "list_of_changes",
                    "customer_address",
                ]
            ]
        )
        loc = [
            field
            for field in project_design.report_fields
            if field.name == "list_of_changes"
        ][0]
        assert loc.type == "list"
        assert isinstance(loc.items, ProjectDesignField)
        assert isinstance(loc.items.properties, list)
        property_field_names = [field.name for field in loc.items.properties]
        assert len(property_field_names) == 3
        assert all(
            name in property_field_names for name in ["date", "version", "description"]
        )
        assert isinstance(loc.items.properties[0], ProjectDesignField)
