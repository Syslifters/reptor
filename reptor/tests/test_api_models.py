import json
import unittest

from reptor.api.models import (Finding, FindingData, FindingTemplate, Project,
                               ProjectDesign, ProjectDesignField, User)


class TestModelsParsing(unittest.TestCase):
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

    example_finding_template = """
    {
            "id": "e6961177-0582-4dd2-b057-c48490294ddd",
            "created": "2022-10-19T10:30:48.055519Z",
            "updated": "2023-05-17T07:15:51.700130Z",
            "details": "http://localhost:8000/api/v1/findingtemplates/e6961177-0582-4dd2-b057-c48490294ddd",
            "lock_info": null,
            "usage_count": 1,
            "source": "imported",
            "tags": [
                "web"
            ],
            "language": "en-US",
            "status": "in-progress",
            "data": {
                "title": "SQL Injection (SQLi)",
                "cvss": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "summary": "The web application processed user input in an insecure manner and was thus vulnerable to SQL injection. In an SQL injection attack, special input values in the web application are used to influence the application's SQL statements to its database. Depending on the database used and the design of the application, this may make it possible to read and modify the data stored in the database, perform administrative actions (e.g., shut down the DBMS), or in some cases even gain code execution and the accompanying complete control over the vulnerable server.",
                "description": "We identified an SQL injection vulnerability in the web application and were able to access stored data in the database as a result.  **TODO: technical description**  SQL Injection is a common server-side vulnerability in web applications. It occurs when software developers create dynamic database queries that contain user input. In an attack, user input is crafted in such a way that the originally intended action of an SQL statement is changed. SQL injection vulnerabilities result from an application's failure to dynamically create database queries insecurely and to properly validate user input. They are based on the fact that the SQL language basically does not distinguish between control characters and data characters. In order to use a control character in the data part of an SQL statement, it must be encoded or escaped appropriately beforehand.  An SQL injection attack is therefore essentially carried out by inserting a control character such as `'` (single apostrophe) into the user input to place new commands that were not present in the original SQL statement. A simple example will demonstrate this process. The following SELECT statement contains a variable userId. The purpose of this statement is to get data of a user with a specific user id from the Users table.  `sqlStmnt = 'SELECT * FROM Users WHERE UserId = ' + userId;`  An attacker could now use special user input to change the original intent of the SQL statement. For example, he could use the string `' or 1=1` as user input. In this case, the application would construct the following SQL statement:  `sqlStmnt = 'SELECT * FROM Users WHERE UserId = ' + ' or 1=1;`  Instead of the data of a user with a specific user ID, the data of all users in the table is now returned to the attacker after executing the statement. This gives an attacker the ability to control the SQL statement in his own favor.   There are a number of variants of SQL injection vulnerabilities, attacks and techniques that occur in different situations and depending on the database system used. However, what they all have in common is that, as in the example above, user input is always used to dynamically construct SQL statements. Successful SQL injection attacks can have far-reaching consequences. One would be the loss of confidentiality and integrity of the stored data. Attackers could gain read and possibly write access to sensitive data in the database. SQL injection could also compromise the authentication and authorization of the web application, allowing attackers to bypass existing access controls. In some cases, SQL injection can also be used to gain code execution, allowing an attacker to gain complete control over the vulnerable server.",
                "precondition": null,
                "impact": null,
                "recommendation": "* Use prepared statements throughout the application to effectively avoid SQL injection vulnerabilities. Prepared statements are parameterized statements and ensure that even if input values are manipulated, an attacker is unable to change the original intent of an SQL statement.  * Use existing stored procedures by default where possible. Typically, stored procedures are implemented as secure parameterized queries and thus protect against SQL injections. * Always validate all user input. Ensure that only input that is expected and valid for the application is accepted. You should not sanitize potentially malicious input. * To reduce the potential damage of a successful SQL Injection attack, you should minimize the assigned privileges of the database user used according to the principle of least privilege. * For detailed information and assistance on how to prevent SQL Injection vulnerabilities, see OWASP's linked SQL Injection Prevention Cheat Sheet.",
                "short_recommendation": "Make sure that Prepared Statements and Stored Procedures (where possible) are used throughout the application. This prevents the originally intended action of an SQL statement from being manipulated by an attacker.",
                "references": [
                    "https://www.owasp.org/index.php/SQL_Injection_Prevention_Cheat_Sheet"
                ],
                "affected_components": [],
                "owasp_top10_2021": null,
                "wstg_category": null,
                "retest_notes": null,
                "retest_status": null
            }
        }"""

    example_project_design = """
    {"id":"9ef57060-9bcc-4410-b1fd-744d7657558c","created":"2023-07-14T14:19:06.805883Z","updated":"2023-07-14T15:35:05.162391Z","source":"created","scope":"private","name":"Demo Report v1.12","language":"en-US","details":"https://demo.sysre.pt/api/v1/projecttypes/9ef57060-9bcc-4410-b1fd-744d7657558c","assets":"https://demo.sysre.pt/api/v1/projecttypes/9ef57060-9bcc-4410-b1fd-744d7657558c/assets","copy_of":"da029ad9-ee5b-4f31-820e-a0e48ddbc8b8","lock_info":{"created":"2023-07-14T17:18:19.072853Z","updated":"2023-07-14T17:18:49.380931Z","last_ping":"2023-07-14T17:18:49.380870Z","expires":"2023-07-14T17:20:19.380870Z","user":{"id":"80bcd0a1-4a7d-4288-9853-8592662c8ee3","username":"demo-eoNeCdnO","name":"","title_before":null,"first_name":"","middle_name":null,"last_name":"","title_after":null,"is_active":true}},"report_template":"","report_preview_data":{"report":{"pta":"TODO: screenshots of PTA"},"findings":[{"id":"a10eed1a-07f5-46ef-bf3a-b78208e72272","cvss":"CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H","title":"Demo Finding Critical","summary":"TODO summary","references":["https://example.com"],"description":"TODO description","wstg_category":"IDNT","recommendation":"TODO recommendation","affected_components":["https://example.com"],"recomlist":["quidem aliquam","est possimus"],"new_field1":{"date":"2023-07-14","enum":"enum_val","user":null,"new_cvss":"n/a","new_field2":"sed laudantium","new_field4":"quam similique","nested_field":"Combobox Value"},"importantenum":"enum_val"}]},"report_fields":{"draft":{"type":"boolean","label":"Is Draft?","origin":"custom","default":true},"scope":{"type":"markdown","label":"Scope","origin":"custom","default":"**TODO:","required":true},"title":{"type":"string","label":"Title","origin":"core","default":"TODO report title","required":true,"spellcheck":false},"duration":{"type":"string","label":"Duration","origin":"custom","default":"TODO person days","required":true,"spellcheck":false},"end_date":{"type":"date","label":"Pentest End Date","origin":"custom","default":null,"required":true},"start_date":{"type":"date","label":"Pentest Start Date","origin":"custom","default":null,"required":true},"report_date":{"type":"date","label":"Report Date","origin":"custom","default":null,"required":true},"customer_name":{"type":"string","label":"Customer","origin":"custom","default":"TODO company","required":true,"spellcheck":false},"receiver_name":{"type":"string","label":"Receiver Name","origin":"custom","default":"TODO receiver","required":true,"spellcheck":false},"provided_users":{"type":"markdown","label":"Users and Permissions","origin":"custom","default":"**TODO: Provided Use","required":true},"report_version":{"type":"string","label":"Report Version","origin":"custom","default":"1.0","required":true,"spellcheck":false},"list_of_changes":{"type":"list","items":{"type":"object","label":"","origin":"custom","properties":{"date":{"type":"date","label":"Date","origin":"custom","default":null,"required":true},"version":{"type":"string","label":"Version","origin":"custom","default":"TODO version","required":true,"spellcheck":false},"description":{"type":"string","label":"Description","origin":"custom","default":"TODO description","required":true,"spellcheck":false}}},"label":"List of Changes","origin":"custom","required":true},"customer_address":{"type":"object","label":"Address","origin":"custom","properties":{"city":{"type":"string","label":"City","origin":"custom","default":"TODO city","required":true,"spellcheck":false},"street":{"type":"string","label":"Street","origin":"custom","default":"TODO street","required":true,"spellcheck":false}}},"appendix_sections":{"type":"list","items":{"type":"object","label":"","origin":"custom","properties":{"title":{"type":"string","label":"Title","origin":"custom","default":"TODO appendix title","required":true,"spellcheck":false},"content":{"type":"markdown","label":"Content","origin":"custom","default":"TODO appendix content","required":true}}},"label":"Appendix","origin":"custom","required":true},"executive_summary":{"type":"markdown","label":"Executive Summary","origin":"custom","default":"**TODO:","required":true}},"report_sections":[{"id":"executive_summary","label":"Executive Summary","fields":["executive_summary"]},{"id":"scope","label":"Scope","fields":["scope","start_date","end_date","duration","provided_users"]},{"id":"customer","label":"Customer","fields":["customer_name","customer_address","receiver_name"]},{"id":"other","label":"Other","fields":["title","report_date","report_version","list_of_changes","draft"]},{"id":"appendix","label":"Appendix","fields":["appendix_sections"]}],"finding_fields":{"cvss":{"type":"cvss","label":"CVSS","origin":"core","default":"n/a","required":true},"title":{"type":"string","label":"Titel","origin":"core","default":"TODO finding title","required":true,"spellcheck":false},"summary":{"type":"markdown","label":"Overview","origin":"predefined","default":"TODO summary","required":true},"recomlist":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"recomlist","origin":"custom","required":true},"new_field1":{"type":"object","label":"New Field","origin":"custom","properties":{"date":{"type":"date","label":"New Field","origin":"custom","default":"2023-07-14","required":true},"enum":{"type":"enum","label":"New Field","origin":"custom","choices":[{"label":"Enum Value","value":"enum_val"},{"label":"New Enum Value","value":"new_value1"}],"default":null,"required":true},"user":{"type":"user","label":"New Field","origin":"custom","required":false},"new_cvss":{"type":"cvss","label":"New Field","origin":"custom","default":"n/a","required":true},"new_field2":{"type":"string","label":"New Field","origin":"custom","default":null,"required":true,"spellcheck":false},"new_field4":{"type":"string","label":"New Field","origin":"custom","default":null,"required":true,"spellcheck":false},"nested_field":{"type":"combobox","label":"Nested Field","origin":"custom","default":null,"required":true,"suggestions":["Combobox Value"]}}},"references":{"type":"list","items":{"type":"string","label":"Reference","origin":"predefined","default":"TODO reference","required":true,"spellcheck":false},"label":"References","origin":"predefined","required":false},"description":{"type":"markdown","label":"Details","origin":"predefined","default":"TODO description","required":true},"importantenum":{"type":"enum","label":"importantenum","origin":"custom","choices":[{"label":"Enum Value","value":"enum_val"},{"label":"New Enum Value","value":"new_value1"},{"label":"New Enum Value","value":"new_value1"}],"default":null,"required":true},"recommendation":{"type":"markdown","label":"Recommendation","origin":"predefined","default":"TODO recommendation","required":true},"affected_components":{"type":"list","items":{"type":"string","label":"Component","origin":"predefined","default":"TODO affected component","required":true,"spellcheck":false},"label":"Affected Components","origin":"predefined","required":true}},"finding_field_order":["title","cvss","references","affected_components","summary","description","recommendation","importantenum","recomlist","new_field1"]}"""

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

    def test_finding_parsing(self):
        api_test_data = json.loads(self.example_finding)
        finding = Finding(api_test_data)
        self.assertEqual(finding.id, "d3658ee5-2d43-40f6-9b97-1b98480afe78")
        self.assertEqual(finding.language, "en-US")
        self.assertEqual(finding.project_type,
                         "2970149f-e11d-420a-8a5d-25b5fda14e33")
        self.assertIsInstance(finding.assignee, dict)
        self.assertIsInstance(finding.data, FindingData)
        self.assertEqual(finding.data.cvss, "n/a")
        self.assertEqual(finding.data.title, "My Title")
        self.assertEqual(finding.data.date_field, "2023-07-03")
        self.assertEqual(finding.data.enum_field, "enum_val_2")
        self.assertIsInstance(finding.data.list_field, list)
        self.assertEqual(len(finding.data.list_field), 2)
        self.assertEqual(finding.data.list_field[0], {
                         "enum_in_object": "enum_in_obj_2"})
        self.assertEqual(finding.data.user_field,
                         "788dcb76-9928-46fc-87ba-7043708f1bc0")
        self.assertEqual(finding.data.number_field, 1337.0)
        self.assertIsInstance(finding.data.number_field, float)
        self.assertIsInstance(finding.data.object_field, dict)
        self.assertIn('list_in_object', finding.data.object_field)
        self.assertEqual(len(finding.data.object_field['list_in_object']), 2)
        self.assertEqual(
            finding.data.object_field['list_in_object'][0], "My String in List in Object")
        self.assertEqual(finding.data.boolean_field, True)
        self.assertEqual(finding.data.combobox_field, "Combobox Value 2")
        self.assertEqual(finding.data.markdown_field, "My Markdown")
        # print(finding.data)

    def test_project_design_parsing(self):
        api_test_data = json.loads(self.example_project_design)
        project_design = ProjectDesign(api_test_data)
        self.assertEqual(project_design.id,
                         '9ef57060-9bcc-4410-b1fd-744d7657558c')
        self.assertEqual(project_design.source, 'created')
        self.assertEqual(project_design.scope, 'private')
        self.assertEqual(project_design.name, 'Demo Report v1.12')
        self.assertEqual(project_design.language, 'en-US')
        self.assertIsInstance(project_design.finding_fields, list)
        self.assertIsInstance(project_design.report_fields, list)
        self.assertEqual(len(project_design.finding_fields), 10)
        self.assertEqual(len(project_design.report_fields), 15)

        report_field_names = [
            field.name for field in project_design.report_fields]
        self.assertTrue(all([name in report_field_names for name in ['draft', 'scope', 'title', 'duration', 'end_date', 'start_date',
                        'report_date', 'customer_name', 'receiver_name', 'provided_users', 'report_version', 'list_of_changes', 'customer_address']]))
        loc = [
            field for field in project_design.report_fields if field.name == 'list_of_changes'][0]
        self.assertEqual(loc.type, 'list')
        self.assertIsInstance(loc.items, ProjectDesignField)
        self.assertIsInstance(loc.items.properties, list)
        property_field_names = [field.name for field in loc.items.properties]
        self.assertEqual(len(property_field_names), 3)
        self.assertTrue(all(name in property_field_names for name in [
                        'date', 'version', 'description']))
        self.assertIsInstance(loc.items.properties[0], ProjectDesignField)

    def test_user_parsing(self):
        api_test_data = json.loads(self.example_user)

        test_user = User(api_test_data)

        self.assertEqual(test_user.id, "e79abf41-5b7c-4c1f-826e-040f34eaf6b4")
        self.assertEqual(test_user.name, "Richard Schwabe")
        self.assertEqual(test_user.first_name, "Richard")
        self.assertEqual(test_user.last_name, "Schwabe")
        self.assertEqual(test_user.is_superuser, True)
        self.assertTrue(test_user.scope)

    def test_project_parsing(self):
        api_test_data = json.loads(self.example_project)

        test_project = Project(api_test_data)
        self.assertEqual(
            test_project.id, "4cf78324-8502-4fb0-936a-724892d3c539")
        self.assertEqual(
            test_project.members[0].id, "f2c9bad4-c916-4c18-9f76-d5ef94b34453"
        )
        self.assertEqual(test_project.members[1].username, "richard")
        self.assertEqual(
            test_project.project_type, "fa670018-e6ef-4b73-989b-1e4c4af09cee"
        )

    def test_finding_template_parsing(self):
        api_test_data = json.loads(self.example_finding_template)

        test_finding_template = FindingTemplate(api_test_data)
        self.assertEqual(
            test_finding_template.id, "e6961177-0582-4dd2-b057-c48490294ddd"
        )
        self.assertEqual(test_finding_template.data.title,
                         "SQL Injection (SQLi)")
        self.assertTrue(test_finding_template.data.references)
        self.assertEqual(
            test_finding_template.data.references[0],
            "https://www.owasp.org/index.php/SQL_Injection_Prevention_Cheat_Sheet",
        )


if __name__ == "__main__":
    unittest.main()
