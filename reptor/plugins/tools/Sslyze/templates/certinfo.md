<!--{% load md %}--><!--{% noemptylines %}-->
<!--{% if certinfo.certificate_untrusted %}-->
 * <span style="color: red">Certificate untrusted by:</span>
<!--{% for browser in certinfo.certificate_untrusted %}-->
    * <!--{{ browser }}-->
<!--{% endfor %}-->
<!--{% else %}-->
 * <span style="color: green">Certificate is trusted</span>
<!--{% endif %}-->
 * Certificate matches hostname: <span style="color: <!--{% if certinfo.certificate_matches_hostname %}-->green<!--{% else %}-->red<!--{% endif %}-->"><!--{{ certinfo.certificate_matches_hostname|yesno:"Yes,No" }}--></span>
 * SHA1 in certificate chain: <span style="color: <!--{% if certinfo.has_sha1_in_certificate_chain %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ certinfo.has_sha1_in_certificate_chain|yesno:"Yes,No" }}--></span>
<!--{% endnoemptylines %}-->
