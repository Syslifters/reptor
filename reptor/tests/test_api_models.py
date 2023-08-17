import json
from copy import deepcopy

import pytest

from reptor.api.models import (
    FindingData,
    FindingDataField,
    FindingDataRaw,
    FindingRaw,
    FindingTemplate,
    Project,
    ProjectDesign,
    ProjectDesignField,
    SectionData,
    SectionDataField,
    SectionRaw,
    User,
)


class TestModelsParsing:
    example_user = """
{
            "id": "e79abf41-5b7c-4c1f-826e-040f34eaf6b4",
            "created": "2023-05-19T08:19:23.679429Z",
            "updated": "2023-05-19T08:19:23.680725Z",
            "last_login": null,
            "is_active": true,
            "username": "rs",
            "name": "Richard Schwabe",
            "title_before": null,
            "first_name": "Richard",
            "middle_name": null,
            "last_name": "Schwabe",
            "title_after": null,
            "email": null,
            "phone": null,
            "mobile": null,
            "scope": [
                "admin",
                "template_editor",
                "designer",
                "user_manager"
            ],
            "is_superuser": true,
            "is_designer": false,
            "is_template_editor": false,
            "is_user_manager": false,
            "is_guest": false,
            "is_system_user": false,
            "is_global_archiver": false,
            "is_mfa_enabled": false,
            "can_login_local": true,
            "can_login_sso": false
        }
        """

    example_project = """
    {
            "id": "4cf78324-8502-4fb0-936a-724892d3c539",
            "created": "2023-06-16T19:12:00.478314Z",
            "updated": "2023-06-25T13:49:48.935500Z",
            "name": "PNPT Exam",
            "project_type": "fa670018-e6ef-4b73-989b-1e4c4af09cee",
            "language": "en-US",
            "tags": [],
            "readonly": true,
            "source": "created",
            "copy_of": null,
            "members": [
                {
                    "id": "f2c9bad4-c916-4c18-9f76-d5ef94b34453",
                    "username": "reptor",
                    "name": "Bjoern Schwabe",
                    "title_before": "",
                    "first_name": "Bjoern",
                    "middle_name": null,
                    "last_name": "Schwabe",
                    "title_after": "",
                    "is_active": true,
                    "roles": [
                        "pentester"
                    ]
                },

                {
                    "id": "f2c9bad4-c916-4c18-9f76-d5ef94b34454",
                    "username": "richard",
                    "name": "Richard Schwabe",
                    "title_before": "",
                    "first_name": "Richard",
                    "middle_name": null,
                    "last_name": "Schwabe",
                    "title_after": "",
                    "is_active": true,
                    "roles": [
                        "pentester"
                    ]
                }
            ],
            "imported_members": [],
            "details": "http://localhost:8000/api/v1/pentestprojects/4cf78324-8502-4fb0-936a-724892d3c539",
            "findings": "http://localhost:8000/api/v1/pentestprojects/4cf78324-8502-4fb0-936a-724892d3c539/findings",
            "sections": "http://localhost:8000/api/v1/pentestprojects/4cf78324-8502-4fb0-936a-724892d3c539/sections",
            "notes": "http://localhost:8000/api/v1/pentestprojects/4cf78324-8502-4fb0-936a-724892d3c539/notes",
            "images": "http://localhost:8000/api/v1/pentestprojects/4cf78324-8502-4fb0-936a-724892d3c539/images"
        }"""

    example_finding_template = '{"id":"82c5d4c5-b1ff-4d17-9567-c2679df325d5","created":"2022-10-19T10:30:48.055000Z","updated":"2023-07-24T10:19:59.815926Z","details":"https://syslifters.sysre.pt/api/v1/findingtemplates/82c5d4c5-b1ff-4d17-9567-c2679df325d5","images":"https://syslifters.sysre.pt/api/v1/findingtemplates/82c5d4c5-b1ff-4d17-9567-c2679df325d5/images","usage_count":14,"source":"created","tags":["web"],"translations":[{"id":"7171d2ef-a2ca-4710-9fea-6689ff2b9a26","created":"2023-07-24T10:19:59.813648Z","updated":"2023-07-24T10:19:59.813885Z","language":"en-US","status":"finished","is_main":true,"risk_score":9.8,"risk_level":"critical","data":{"title":"SQL Injection (SQLi)","cvss":"CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H","summary":"The web application processed user input in an insecure manner and was thus vulnerable to SQL injection. In an SQL injection attack, special input values in the web application are used to influence the application\'s SQL statements to its database. Depending on the database used and the design of the application, this may make it possible to read and modify the data stored in the database, perform administrative actions (e.g., shut down the DBMS), or in some cases even gain code execution and the accompanying complete control over the vulnerable server.","description":"We identified an SQL injection vulnerability in the web application and were able to access stored data in the database as a result.\\n\\n**TODO: technical description**\\n\\nSQL Injection is a common server-side vulnerability in web applications. It occurs when software developers create dynamic database queries that contain user input. In an attack, user input is crafted in such a way that the originally intended action of an SQL statement is changed. SQL injection vulnerabilities result from an application\'s failure to dynamically create database queries insecurely and to properly validate user input. They are based on the fact that the SQL language basically does not distinguish between control characters and data characters. In order to use a control character in the data part of an SQL statement, it must be encoded or escaped appropriately beforehand.\\n\\nAn SQL injection attack is therefore essentially carried out by inserting a control character such as `\'` (single apostrophe) into the user input to place new commands that were not present in the original SQL statement. A simple example will demonstrate this process. The following SELECT statement contains a variable userId. The purpose of this statement is to get data of a user with a specific user id from the Users table.\\n\\n`sqlStmnt = \'SELECT * FROM Users WHERE UserId = \' + userId;`\\n\\nAn attacker could now use special user input to change the original intent of the SQL statement. For example, he could use the string `\' or 1=1` as user input. In this case, the application would construct the following SQL statement:\\n\\n`sqlStmnt = \'SELECT * FROM Users WHERE UserId = \' + \' or 1=1;`\\n\\nInstead of the data of a user with a specific user ID, the data of all users in the table is now returned to the attacker after executing the statement. This gives an attacker the ability to control the SQL statement in his own favor. \\n\\nThere are a number of variants of SQL injection vulnerabilities, attacks and techniques that occur in different situations and depending on the database system used. However, what they all have in common is that, as in the example above, user input is always used to dynamically construct SQL statements. Successful SQL injection attacks can have far-reaching consequences. One would be the loss of confidentiality and integrity of the stored data. Attackers could gain read and possibly write access to sensitive data in the database. SQL injection could also compromise the authentication and authorization of the web application, allowing attackers to bypass existing access controls. In some cases, SQL injection can also be used to gain code execution, allowing an attacker to gain complete control over the vulnerable server.","precondition":null,"impact":null,"recommendation":"* Use prepared statements throughout the application to effectively avoid SQL injection vulnerabilities. Prepared statements are parameterized statements and ensure that even if input values are manipulated, an attacker is unable to change the original intent of an SQL statement. \\n* Use existing stored procedures by default where possible. Typically, stored procedures are implemented as secure parameterized queries and thus protect against SQL injections.\\n* Always validate all user input. Ensure that only input that is expected and valid for the application is accepted. You should not sanitize potentially malicious input.\\n* To reduce the potential damage of a successful SQL Injection attack, you should minimize the assigned privileges of the database user used according to the principle of least privilege.\\n* For detailed information and assistance on how to prevent SQL Injection vulnerabilities, see OWASP\'s linked SQL Injection Prevention Cheat Sheet.","short_recommendation":"Make sure that Prepared Statements and Stored Procedures (where possible) are used throughout the application. This prevents the originally intended action of an SQL statement from being manipulated by an attacker.","references":["https://www.owasp.org/index.php/SQL_Injection_Prevention_Cheat_Sheet"],"affected_components":[],"owasp_top10_2021":null,"wstg_category":null,"retest_notes":null,"retest_status":null,"retest":null,"retest_state":null}},{"id":"e1aa87ee-7eed-4f47-b730-ab4b255d7abe","created":"2023-08-11T11:23:04.659627Z","updated":"2023-08-11T11:23:04.661221Z","language":"de-DE","status":"in-progress","is_main":false,"risk_score":0.0,"risk_level":"info","data":{"title":"Template Titel","summary":"Auch test."}}],"lock_info":null}'

    example_project_design = """
    {"id":"9ef57060-9bcc-4410-b1fd-744d7657558c","created":"2023-07-14T14:19:06.805883Z","updated":"2023-07-14T15:35:05.162391Z","source":"created","scope":"private","name":"Demo Report v1.12","language":"en-US","details":"https://demo.sysre.pt/api/v1/projecttypes/9ef57060-9bcc-4410-b1fd-744d7657558c","assets":"https://demo.sysre.pt/api/v1/projecttypes/9ef57060-9bcc-4410-b1fd-744d7657558c/assets","copy_of":"da029ad9-ee5b-4f31-820e-a0e48ddbc8b8","lock_info":{"created":"2023-07-14T17:18:19.072853Z","updated":"2023-07-14T17:18:49.380931Z","last_ping":"2023-07-14T17:18:49.380870Z","expires":"2023-07-14T17:20:19.380870Z","user":{"id":"80bcd0a1-4a7d-4288-9853-8592662c8ee3","username":"demo-eoNeCdnO","name":"","title_before":null,"first_name":"","middle_name":null,"last_name":"","title_after":null,"is_active":true}},"report_template":"","report_preview_data":{"report":{"pta":"TODO: screenshots of PTA"},"findings":[{"id":"a10eed1a-07f5-46ef-bf3a-b78208e72272","cvss":"CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H","title":"Demo Finding Critical","summary":"TODO summary","references":["https://example.com"],"description":"TODO description","wstg_category":"IDNT","recommendation":"TODO recommendation","affected_components":["https://example.com"],"recomlist":["quidem aliquam","est possimus"],"new_field1":{"date":"2023-07-14","enum":"enum_val","user":null,"new_cvss":"n/a","new_field2":"sed laudantium","new_field4":"quam similique","nested_field":"Combobox Value"},"importantenum":"enum_val"}]},"report_fields":{"draft":{"type":"boolean","label":"Is Draft?","origin":"custom","default":true},"scope":{"type":"markdown","label":"Scope","origin":"custom","default":"**TODO:","required":true},"title":{"type":"string","label":"Title","origin":"core","default":"TODO report title","required":true,"spellcheck":false},"duration":{"type":"string","label":"Duration","origin":"custom","default":"TODO person days","required":true,"spellcheck":false},"end_date":{"type":"date","label":"Pentest End Date","origin":"custom","default":null,"required":true},"start_date":{"type":"date","label":"Pentest Start Date","origin":"custom","default":null,"required":true},"report_date":{"type":"date","label":"Report Date","origin":"custom","default":null,"required":true},"customer_name":{"type":"string","label":"Customer","origin":"custom","default":"TODO company","required":true,"spellcheck":false},"receiver_name":{"type":"string","label":"Receiver Name","origin":"custom","default":"TODO receiver","required":true,"spellcheck":false},"provided_users":{"type":"markdown","label":"Users and Permissions","origin":"custom","default":"**TODO: Provided Use","required":true},"report_version":{"type":"string","label":"Report Version","origin":"custom","default":"1.0","required":true,"spellcheck":false},"list_of_changes":{"type":"list","items":{"type":"object","label":"","origin":"custom","properties":{"date":{"type":"date","label":"Date","origin":"custom","default":null,"required":true},"version":{"type":"string","label":"Version","origin":"custom","default":"TODO version","required":true,"spellcheck":false},"description":{"type":"string","label":"Description","origin":"custom","default":"TODO description","required":true,"spellcheck":false}}},"label":"List of Changes","origin":"custom","required":true},"customer_address":{"type":"object","label":"Address","origin":"custom","properties":{"city":{"type":"string","label":"City","origin":"custom","default":"TODO city","required":true,"spellcheck":false},"street":{"type":"string","label":"Street","origin":"custom","default":"TODO street","required":true,"spellcheck":false}}},"appendix_sections":{"type":"list","items":{"type":"object","label":"","origin":"custom","properties":{"title":{"type":"string","label":"Title","origin":"custom","default":"TODO appendix title","required":true,"spellcheck":false},"content":{"type":"markdown","label":"Content","origin":"custom","default":"TODO appendix content","required":true}}},"label":"Appendix","origin":"custom","required":true},"executive_summary":{"type":"markdown","label":"Executive Summary","origin":"custom","default":"**TODO:","required":true}},"report_sections":[{"id":"executive_summary","label":"Executive Summary","fields":["executive_summary"]},{"id":"scope","label":"Scope","fields":["scope","start_date","end_date","duration","provided_users"]},{"id":"customer","label":"Customer","fields":["customer_name","customer_address","receiver_name"]},{"id":"other","label":"Other","fields":["title","report_date","report_version","list_of_changes","draft"]},{"id":"appendix","label":"Appendix","fields":["appendix_sections"]}],"finding_fields":{"cvss":{"type":"cvss","label":"CVSS","origin":"core","default":"n/a","required":true},"title":{"type":"string","label":"Titel","origin":"core","default":"TODO finding title","required":true,"spellcheck":false},"summary":{"type":"markdown","label":"Overview","origin":"predefined","default":"TODO summary","required":true},"recomlist":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"recomlist","origin":"custom","required":true},"new_field1":{"type":"object","label":"New Field","origin":"custom","properties":{"date":{"type":"date","label":"New Field","origin":"custom","default":"2023-07-14","required":true},"enum":{"type":"enum","label":"New Field","origin":"custom","choices":[{"label":"Enum Value","value":"enum_val"},{"label":"New Enum Value","value":"new_value1"}],"default":null,"required":true},"user":{"type":"user","label":"New Field","origin":"custom","required":false},"new_cvss":{"type":"cvss","label":"New Field","origin":"custom","default":"n/a","required":true},"new_field2":{"type":"string","label":"New Field","origin":"custom","default":null,"required":true,"spellcheck":false},"new_field4":{"type":"string","label":"New Field","origin":"custom","default":null,"required":true,"spellcheck":false},"nested_field":{"type":"combobox","label":"Nested Field","origin":"custom","default":null,"required":true,"suggestions":["Combobox Value"]}}},"references":{"type":"list","items":{"type":"string","label":"Reference","origin":"predefined","default":"TODO reference","required":true,"spellcheck":false},"label":"References","origin":"predefined","required":false},"description":{"type":"markdown","label":"Details","origin":"predefined","default":"TODO description","required":true},"importantenum":{"type":"enum","label":"importantenum","origin":"custom","choices":[{"label":"Enum Value","value":"enum_val"},{"label":"New Enum Value","value":"new_value1"},{"label":"New Enum Value","value":"new_value1"}],"default":null,"required":true},"recommendation":{"type":"markdown","label":"Recommendation","origin":"predefined","default":"TODO recommendation","required":true},"affected_components":{"type":"list","items":{"type":"string","label":"Component","origin":"predefined","default":"TODO affected component","required":true,"spellcheck":false},"label":"Affected Components","origin":"predefined","required":true}},"finding_field_order":["title","cvss","references","affected_components","summary","description","recommendation","importantenum","recomlist","new_field1"]}"""

    example_design_with_finding_fields_only = """
    {"finding_fields":{"cvss":{"type":"cvss","label":"CVSS","origin":"core","default":"n/a","required":true},"title":{"type":"string","label":"Title","origin":"core","default":"TODO: Finding Title","required":true,"spellcheck":true},"date_field":{"type":"date","label":"Date Field","origin":"custom","default":null,"required":true},"enum_field":{"type":"enum","label":"Enum Field","origin":"custom","choices":[{"label":"Enum Value 1","value":"enum_val_1"},{"label":"Enum Value 2","value":"enum_val_2"},{"label":"Enum Value 3","value":"enum_val_"}],"default":null,"required":true},"list_field":{"type":"list","items":{"type":"object","label":"","origin":"custom","properties":{"enum_in_object":{"type":"enum","label":"Enum in Object","origin":"custom","choices":[{"label":"Enum in Obj 1","value":"enum_in_obj_1"},{"label":"Enum in Obj 2","value":"enum_in_obj_2"},{"label":"Enum in Obj 3","value":"enum_in_obj_3"}],"default":null,"required":true}}},"label":"List Field","origin":"custom","required":true},"user_field":{"type":"user","label":"User Field","origin":"custom","required":true},"number_field":{"type":"number","label":"Number Field","origin":"custom","default":null,"required":true},"object_field":{"type":"object","label":"Object Field","origin":"custom","properties":{"list_in_object":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"List in Object","origin":"custom","required":true}}},"boolean_field":{"type":"boolean","label":"Boolean Field","origin":"custom","default":null},"combobox_field":{"type":"combobox","label":"Combobox Field","origin":"custom","default":null,"required":true,"suggestions":["Combobox Value 1","Combobox Value 2","Combobox Value 3"]},"markdown_field":{"type":"markdown","label":"Markdown Field","origin":"custom","default":null,"required":true}}}"""

    example_finding = """
    {
        "id": "d3658ee5-2d43-40f6-9b97-1b98480afe78",
        "created": "2023-07-16T20:07:36.213385Z",
        "updated": "2023-07-16T20:08:59.749591Z",
        "project": "a4b4b630-fc78-452d-b348-d362b69c2449",
        "project_type": "2970149f-e11d-420a-8a5d-25b5fda14e33",
        "language": "en-US",
        "lock_info": null,
        "template": null,
        "assignee": {
            "id": "788dcb76-9928-46fc-87ba-7043708f1bc0",
            "username": "demo-fTaIO4fj",
            "name": "",
            "title_before": null,
            "first_name": "",
            "middle_name": null,
            "last_name": "",
            "title_after": null,
            "is_active": true
        },
        "status": "in-progress",
        "data": {
            "cvss": "n/a",
            "title": "My Title",
            "date_field": "2023-07-03",
            "enum_field": "enum_val_2",
            "list_field": [
                {
                    "enum_in_object": "enum_in_obj_2"
                },
                {
                    "enum_in_object": "enum_in_obj_3"
                }
            ],
            "user_field": "788dcb76-9928-46fc-87ba-7043708f1bc0",
            "number_field": 1337.0,
            "object_field": {
                "list_in_object": [
                    "My String in List in Object",
                    "Other String in List in Object"
                ]
            },
            "boolean_field": true,
            "combobox_field": "Combobox Value 2",
            "markdown_field": "My Markdown"
        }
    }"""

    example_design_with_report_fields_only = """
    {
	"report_fields": {
		"draft": {
			"type": "boolean",
			"label": "Is Draft?",
			"origin": "custom",
			"default": true
		},
		"title": {
			"type": "string",
			"label": "Title",
			"origin": "core",
			"default": "TODO report title",
			"required": true,
			"spellcheck": false
		},
		"report_date": {
			"type": "date",
			"label": "Report Date",
			"origin": "custom",
			"default": null,
			"required": true
		},
		"report_version": {
			"type": "string",
			"label": "Report Version",
			"origin": "custom",
			"default": "1.0",
			"required": true,
			"spellcheck": false
		},
		"list_of_changes": {
			"type": "list",
			"items": {
				"type": "object",
				"label": "",
				"origin": "custom",
				"properties": {
					"date": {
						"type": "date",
						"label": "Date",
						"origin": "custom",
						"default": null,
						"required": true
					},
					"version": {
						"type": "string",
						"label": "Version",
						"origin": "custom",
						"default": "TODO version",
						"required": true,
						"spellcheck": false
					},
					"description": {
						"type": "string",
						"label": "Description",
						"origin": "custom",
						"default": "TODO description",
						"required": true,
						"spellcheck": false
					}
				}
			},
			"label": "List of Changes",
			"origin": "custom",
			"required": true   
        }
    }}
    """

    example_section = """
    {
        "id": "other",
        "label": "Other",
        "fields": [
            "title",
            "report_date",
            "report_version",
            "list_of_changes",
            "draft"
        ],
        "project": "42c2f73a-4383-4ec2-a3fa-281598edb0e8",
        "project_type": "53c185f9-b8f3-44e3-ba4d-03a960cb795a",
        "language": "en-US",
        "lock_info": null,
        "assignee": null,
        "status": "in-progress",
        "data": {
            "title": "Test",
            "report_date": "2023-07-31",
            "report_version": "1.0",
            "list_of_changes": [
                {
                    "date": "2023-07-24",
                    "version": "1.0",
                    "description": "Description"
                },
                {
                    "date": "2023-07-25",
                    "version": "2.0",
                    "description": "New Description"
                }
            ],
            "draft": true
        }
    }"""

    def test_section_data(self):
        json_example = json.loads(self.example_section)
        section_raw = SectionRaw(json_example)
        project_design = ProjectDesign(
            json.loads(self.example_design_with_report_fields_only)
        )
        section_data = SectionData(project_design.report_fields, section_raw.data)
        assert section_data.draft.name == "draft"
        assert section_data.draft.type == "boolean"
        assert section_data.draft.value == True

        assert section_data.title.name == "title"
        assert section_data.title.type == "string"
        assert section_data.title.value == "Test"

        assert section_data.report_date.name == "report_date"
        assert section_data.report_date.type == "date"
        assert section_data.report_date.value == "2023-07-31"

        assert section_data.report_version.name == "report_version"
        assert section_data.report_version.type == "string"
        assert section_data.report_version.value == "1.0"

        assert section_data.list_of_changes.name == "list_of_changes"
        assert section_data.list_of_changes.type == "list"
        assert isinstance(section_data.list_of_changes.value[0], SectionDataField)
        assert section_data.list_of_changes.value[0].type == "object"
        assert isinstance(
            section_data.list_of_changes.value[0].value["date"], SectionDataField
        )
        assert section_data.list_of_changes.value[0].value["date"].value == "2023-07-24"
        assert section_data.list_of_changes.value[0].value["version"].value == "1.0"
        assert (
            section_data.list_of_changes.value[0].value["description"].value
            == "Description"
        )
        assert section_data.list_of_changes.value[1].value["date"].value == "2023-07-25"
        assert section_data.list_of_changes.value[1].value["version"].value == "2.0"
        assert (
            section_data.list_of_changes.value[1].value["description"].value
            == "New Description"
        )

        # Test setting values
        section_data.title.value = "New Title"
        assert section_data.title.value == "New Title"
        with pytest.raises(ValueError):
            section_data.title.value = 1

        section_data.report_date.value = "2024-08-08"
        assert section_data.report_date.value == "2024-08-08"
        with pytest.raises(ValueError):
            section_data.report_date.value = "new date"

        section_data.draft.value = False
        assert section_data.draft.value == False
        with pytest.raises(ValueError):
            section_data.draft.value = "False"

        section_data.list_of_changes.value[1].value["date"].value = "2025-01-01"
        assert section_data.list_of_changes.value[1].value["date"].value == "2025-01-01"
        with pytest.raises(ValueError):
            section_data.list_of_changes.value[0].value = "Invalid Value"
        with pytest.raises(ValueError):
            section_data.list_of_changes.value[0].value = {"abc": "test"}

    def test_finding_data(self):
        json_example = json.loads(self.example_finding)
        finding_raw = FindingRaw(json_example)
        project_design = ProjectDesign(
            json.loads(self.example_design_with_finding_fields_only)
        )
        finding_data = FindingData(project_design.finding_fields, finding_raw.data)
        assert finding_data.boolean_field.name == "boolean_field"
        assert finding_data.boolean_field.type == "boolean"
        assert finding_data.boolean_field.value == True

        assert finding_data.combobox_field.name == "combobox_field"
        assert finding_data.combobox_field.type == "combobox"
        assert finding_data.combobox_field.value == "Combobox Value 2"

        assert finding_data.cvss.name == "cvss"
        assert finding_data.cvss.type == "cvss"
        assert finding_data.cvss.value == "n/a"

        assert finding_data.date_field.name == "date_field"
        assert finding_data.date_field.type == "date"
        assert finding_data.date_field.value == "2023-07-03"

        assert finding_data.enum_field.name == "enum_field"
        assert finding_data.enum_field.type == "enum"
        assert finding_data.enum_field.value == "enum_val_2"

        assert finding_data.list_field.name == "list_field"
        assert finding_data.list_field.type == "list"
        assert isinstance(finding_data.list_field.value, list)
        assert isinstance(finding_data.list_field.value[0], FindingDataField)
        assert finding_data.list_field.value[0].type == "object"
        assert isinstance(finding_data.list_field.value[0].value, dict)
        assert isinstance(
            finding_data.list_field.value[0].value["enum_in_object"], FindingDataField
        )
        assert finding_data.list_field.value[0].value["enum_in_object"].type == "enum"
        assert (
            finding_data.list_field.value[0].value["enum_in_object"].value
            == "enum_in_obj_2"
        )
        assert finding_data.object_field.name == "object_field"
        assert finding_data.object_field.type == "object"
        assert isinstance(finding_data.object_field.value, dict)
        assert isinstance(
            finding_data.object_field.value["list_in_object"], FindingDataField
        )
        assert finding_data.object_field.value["list_in_object"].type == "list"
        assert isinstance(finding_data.object_field.value["list_in_object"].value, list)
        assert isinstance(
            finding_data.object_field.value["list_in_object"].value[0], FindingDataField
        )
        assert (
            finding_data.object_field.value["list_in_object"].value[0].type == "string"
        )
        assert (
            finding_data.object_field.value["list_in_object"].value[0].value
            == "My String in List in Object"
        )

        assert finding_data.to_json() == json_example["data"]

        # Try to set attributes
        finding_data.enum_field.value = "enum_val_1"
        assert finding_data.enum_field.value == "enum_val_1"
        with pytest.raises(ValueError):
            finding_data.enum_field.value = "invalid_value"

        finding_data.boolean_field.value = False
        assert finding_data.boolean_field.value == False
        with pytest.raises(ValueError):
            finding_data.boolean_field.value = "invalid_value"

        finding_data.combobox_field.value = "Combobox Value 1"
        assert finding_data.combobox_field.value == "Combobox Value 1"
        with pytest.raises(ValueError):
            finding_data.combobox_field.value = True

        finding_data.date_field.value = "2005-01-01"
        assert finding_data.date_field.value == "2005-01-01"
        with pytest.raises(ValueError):
            finding_data.date_field.value = "2002-01-32"

        new_list = deepcopy(finding_data.list_field.value)
        new_list[0].value["enum_in_object"].value = "enum_in_obj_1"
        finding_data.list_field.value = new_list
        assert finding_data.list_field.value == new_list
        with pytest.raises(ValueError):
            # ValueError due to invalid enum
            new_list[0].value["enum_in_object"].value = "invalid_value"
        with pytest.raises(ValueError):
            finding_data.list_field.value = "invalid_value"
        with pytest.raises(ValueError):
            finding_data.list_field.value = [new_list[0], "invalid_value"]
        with pytest.raises(ValueError):
            finding_data.list_field.value = [new_list[0], finding_data.combobox_field]

        new_object = deepcopy(finding_data.object_field.value)
        new_object["list_in_object"].value[0].value = "My new String in List in Object"
        finding_data.object_field.value = new_object
        assert finding_data.object_field.value == new_object
        with pytest.raises(ValueError):
            # ValueError due to invalid string
            new_object["list_in_object"].value[0].value = 1
        with pytest.raises(ValueError):
            finding_data.object_field.value = "invalid_value"
        with pytest.raises(ValueError):
            finding_data.object_field.value = [
                new_object["list_in_object"],
                "invalid_value",
            ]
        with pytest.raises(ValueError):
            finding_data.object_field.value = [
                new_object["list_in_object"],
                finding_data.combobox_field,
            ]

        with pytest.raises(ValueError):
            finding_data.number_field.value = "invalid_value"

        finding_data.user_field.value = "3cb580bd-131b-48f0-9e37-b405e2ab53b8"
        with pytest.raises(ValueError):
            finding_data.user_field.value = "invalid_value"

    def test_finding_raw_parsing(self):
        api_test_data = json.loads(self.example_finding)
        finding = FindingRaw(api_test_data)
        assert finding.id == "d3658ee5-2d43-40f6-9b97-1b98480afe78"
        assert finding.language == "en-US"
        assert finding.project_type == "2970149f-e11d-420a-8a5d-25b5fda14e33"
        assert isinstance(finding.assignee, dict)
        assert isinstance(finding.data, FindingDataRaw)
        assert finding.data.cvss == "n/a"
        assert finding.data.title == "My Title"
        assert finding.data.date_field == "2023-07-03"
        assert finding.data.enum_field == "enum_val_2"
        assert isinstance(finding.data.list_field, list)
        assert len(finding.data.list_field) == 2
        assert finding.data.list_field[0] == {"enum_in_object": "enum_in_obj_2"}
        assert finding.data.user_field == "788dcb76-9928-46fc-87ba-7043708f1bc0"
        assert finding.data.number_field == 1337.0
        assert isinstance(finding.data.number_field, float)
        assert isinstance(finding.data.object_field, dict)
        assert "list_in_object" in finding.data.object_field
        assert len(finding.data.object_field["list_in_object"]) == 2
        assert (
            finding.data.object_field["list_in_object"][0]
            == "My String in List in Object"
        )
        assert finding.data.boolean_field == True
        assert finding.data.combobox_field == "Combobox Value 2"
        assert finding.data.markdown_field == "My Markdown"

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

    def test_user_parsing(self):
        api_test_data = json.loads(self.example_user)

        test_user = User(api_test_data)

        assert test_user.id == "e79abf41-5b7c-4c1f-826e-040f34eaf6b4"
        assert test_user.name == "Richard Schwabe"
        assert test_user.first_name == "Richard"
        assert test_user.last_name == "Schwabe"
        assert test_user.is_superuser == True
        assert test_user.scope

    def test_project_parsing(self):
        api_test_data = json.loads(self.example_project)

        test_project = Project(api_test_data)
        assert test_project.id == "4cf78324-8502-4fb0-936a-724892d3c539"
        assert test_project.members[0].id == "f2c9bad4-c916-4c18-9f76-d5ef94b34453"
        assert test_project.members[1].username == "richard"
        assert test_project.project_type == "fa670018-e6ef-4b73-989b-1e4c4af09cee"

    def test_finding_template_parsing(self):
        api_test_data = json.loads(self.example_finding_template)

        test_finding_template = FindingTemplate(api_test_data)
        assert test_finding_template.id == "82c5d4c5-b1ff-4d17-9567-c2679df325d5"
        assert (
            test_finding_template.translations[0].data.title == "SQL Injection (SQLi)"
        )
        assert test_finding_template.translations[0].data.references
        assert (
            test_finding_template.translations[0].data.references[0]
            == "https://www.owasp.org/index.php/SQL_Injection_Prevention_Cheat_Sheet"
        )
        assert (
            test_finding_template.translations[1].data.title == "Template Titel"
        )
        assert test_finding_template.translations[1].status == "in-progress"
        assert test_finding_template.translations[1].language == "de-DE"