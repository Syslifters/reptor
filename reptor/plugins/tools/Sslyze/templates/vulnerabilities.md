<!--{% load md %}--><!--{% noemptylines %}-->
 * Heartbleed: <span style="color: <!--{{ vulnerabilities.heartbleed|yesno:"red,green" }}-->"><!--{{ vulnerabilities.heartbleed|yesno:"Yes,No" }}--></span>
 * Robot Attack: <span style="color: <!--{{ vulnerabilities.robot|yesno:"red,green" }}-->"><!--{{ vulnerabilities.robot|yesno:"Yes,No" }}--></span>
 * OpenSSL CCS (CVE-2014-0224): <span style="color: <!--{{ vulnerabilities.openssl_ccs|yesno:"red,green" }}-->"><!--{{ vulnerabilities.openssl_ccs|yesno:"Yes,No" }}--></span>
<!--{% endnoemptylines %}-->