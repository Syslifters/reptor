import json
import unittest

from reptor.api.models import User, Project, ProjectType, FindingData, FindingTemplate


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
