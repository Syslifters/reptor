<!--{% load md %}--><!--{% noemptylines %}-->
 * Heartbleed: <span style="color: <!--{% if target.vulnerabilities.heartbleed %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ target.vulnerabilities.heartbleed|yesno:"Yes,No" }}--></span>
 * Robot Attack: <span style="color: <!--{% if target.vulnerabilities.robot %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ target.vulnerabilities.robot|yesno:"Yes,No" }}--></span>
 * OpenSSL CCS (CVE-2014-0224): <span style="color: <!--{% if target.vulnerabilities.openssl_ccs %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ target.vulnerabilities.openssl_ccs|yesno:"Yes,No" }}--></span>
<!--{% endnoemptylines %}-->
