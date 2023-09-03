import json

import pytest

from reptor.models.FindingTemplate import FindingTemplate
from reptor.models.ProjectDesign import ProjectDesign, ProjectDesignField
from reptor.models.Section import SectionData, SectionDataField, SectionRaw


class TestSectionModelParsing:
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

    example_finding_template = '{"id":"82c5d4c5-b1ff-4d17-9567-c2679df325d5","created":"2022-10-19T10:30:48.055000Z","updated":"2023-07-24T10:19:59.815926Z","details":"https://syslifters.sysre.pt/api/v1/findingtemplates/82c5d4c5-b1ff-4d17-9567-c2679df325d5","images":"https://syslifters.sysre.pt/api/v1/findingtemplates/82c5d4c5-b1ff-4d17-9567-c2679df325d5/images","usage_count":14,"source":"created","tags":["web"],"translations":[{"id":"7171d2ef-a2ca-4710-9fea-6689ff2b9a26","created":"2023-07-24T10:19:59.813648Z","updated":"2023-07-24T10:19:59.813885Z","language":"en-US","status":"finished","is_main":true,"risk_score":9.8,"risk_level":"critical","data":{"title":"SQL Injection (SQLi)","cvss":"CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H","summary":"The web application processed user input in an insecure manner and was thus vulnerable to SQL injection. In an SQL injection attack, special input values in the web application are used to influence the application\'s SQL statements to its database. Depending on the database used and the design of the application, this may make it possible to read and modify the data stored in the database, perform administrative actions (e.g., shut down the DBMS), or in some cases even gain code execution and the accompanying complete control over the vulnerable server.","description":"We identified an SQL injection vulnerability in the web application and were able to access stored data in the database as a result.\\n\\n**TODO: technical description**\\n\\nSQL Injection is a common server-side vulnerability in web applications. It occurs when software developers create dynamic database queries that contain user input. In an attack, user input is crafted in such a way that the originally intended action of an SQL statement is changed. SQL injection vulnerabilities result from an application\'s failure to dynamically create database queries insecurely and to properly validate user input. They are based on the fact that the SQL language basically does not distinguish between control characters and data characters. In order to use a control character in the data part of an SQL statement, it must be encoded or escaped appropriately beforehand.\\n\\nAn SQL injection attack is therefore essentially carried out by inserting a control character such as `\'` (single apostrophe) into the user input to place new commands that were not present in the original SQL statement. A simple example will demonstrate this process. The following SELECT statement contains a variable userId. The purpose of this statement is to get data of a user with a specific user id from the Users table.\\n\\n`sqlStmnt = \'SELECT * FROM Users WHERE UserId = \' + userId;`\\n\\nAn attacker could now use special user input to change the original intent of the SQL statement. For example, he could use the string `\' or 1=1` as user input. In this case, the application would construct the following SQL statement:\\n\\n`sqlStmnt = \'SELECT * FROM Users WHERE UserId = \' + \' or 1=1;`\\n\\nInstead of the data of a user with a specific user ID, the data of all users in the table is now returned to the attacker after executing the statement. This gives an attacker the ability to control the SQL statement in his own favor. \\n\\nThere are a number of variants of SQL injection vulnerabilities, attacks and techniques that occur in different situations and depending on the database system used. However, what they all have in common is that, as in the example above, user input is always used to dynamically construct SQL statements. Successful SQL injection attacks can have far-reaching consequences. One would be the loss of confidentiality and integrity of the stored data. Attackers could gain read and possibly write access to sensitive data in the database. SQL injection could also compromise the authentication and authorization of the web application, allowing attackers to bypass existing access controls. In some cases, SQL injection can also be used to gain code execution, allowing an attacker to gain complete control over the vulnerable server.","precondition":null,"impact":null,"recommendation":"* Use prepared statements throughout the application to effectively avoid SQL injection vulnerabilities. Prepared statements are parameterized statements and ensure that even if input values are manipulated, an attacker is unable to change the original intent of an SQL statement. \\n* Use existing stored procedures by default where possible. Typically, stored procedures are implemented as secure parameterized queries and thus protect against SQL injections.\\n* Always validate all user input. Ensure that only input that is expected and valid for the application is accepted. You should not sanitize potentially malicious input.\\n* To reduce the potential damage of a successful SQL Injection attack, you should minimize the assigned privileges of the database user used according to the principle of least privilege.\\n* For detailed information and assistance on how to prevent SQL Injection vulnerabilities, see OWASP\'s linked SQL Injection Prevention Cheat Sheet.","short_recommendation":"Make sure that Prepared Statements and Stored Procedures (where possible) are used throughout the application. This prevents the originally intended action of an SQL statement from being manipulated by an attacker.","references":["https://www.owasp.org/index.php/SQL_Injection_Prevention_Cheat_Sheet"],"affected_components":[],"owasp_top10_2021":null,"wstg_category":null,"retest_notes":null,"retest_status":null,"retest":null,"retest_state":null}},{"id":"e1aa87ee-7eed-4f47-b730-ab4b255d7abe","created":"2023-08-11T11:23:04.659627Z","updated":"2023-08-11T11:23:04.661221Z","language":"de-DE","status":"in-progress","is_main":false,"risk_score":0.0,"risk_level":"info","data":{"title":"Template Titel","summary":"Auch test."}}],"lock_info":null}'

    def test_section_data(self):
        json_example = json.loads(self.example_section)
        section_raw = SectionRaw(json_example)
        project_design = ProjectDesign(
            json.loads(self.example_design_with_report_fields_only)
        )
        section_data = SectionData(section_raw.data, project_design.report_fields)
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
        assert test_finding_template.translations[1].data.title == "Template Titel"
        assert test_finding_template.translations[1].status == "in-progress"
        assert test_finding_template.translations[1].language == "de-DE"

    @pytest.mark.parametrize(
        "type",
        [
            "list",
            "object",
        ],
    )
    def test_list_unsupported_section_data_field(self, type):
        fld = ProjectDesignField(
            {
                "type": "list",
                "items": {"type": type, "items": {"type": "string"}, "properties": {}},
            }
        )
        with pytest.raises(ValueError):
            SectionDataField(fld, "invalid_value")

    @pytest.mark.parametrize(
        "type,value,invalid_value",
        [
            ("string", "test", 12),
            ("cvss", "test", 12),
            ("markdown", "test", 12),
            ("combobox", "test", 12),
            ("user", "3d503331-77d8-4d5e-b3de-e95875f959c4", 12),
            ("user", "3d503331-77d8-4d5e-b3de-e95875f959c4", "12"),
            ("date", "2023-01-01", "12"),
            ("date", "2023-01-31", "2023-01-32"),
            ("date", "2023-01-31", 12),
            ("number", 12, "12"),
            ("boolean", False, "12"),
            ("boolean", True, "true"),
            ("boolean", False, 1),
            ("boolean", False, 0),
            ("enum", "a", "12"),
            ("enum", "b", 12),
            ("enum", "b", False),
        ],
    )
    def test_list_section_data_field(self, type, value, invalid_value):
        fld = ProjectDesignField(
            {
                "choices": [
                    {"label": "A", "value": "a"},
                    {"label": "B", "value": "b"},
                ],
                "type": type,
            }
        )
        SectionDataField(fld, value)
        with pytest.raises(ValueError):
            SectionDataField(fld, invalid_value)
