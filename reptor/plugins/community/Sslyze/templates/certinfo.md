<!--{% load md %}--><!--{% noemptylines %}-->
<!--{% if target.certinfo.certificate_untrusted %}-->
 * <span style="color: red">Certificate untrusted by:</span><!--{% else %}--> * <span style="color: green">Certificate is trusted</span><!--{% endif %}-->
 * Certificate matches hostname: <span style="color: <!--{% if target.certinfo.certificate_matches_hostname %}-->green<!--{% else %}-->red<!--{% endif %}-->"><!--{{ target.certinfo.certificate_matches_hostname|yesno:"Yes,No" }}--></span>
 * SHA1 in certificate chain: <span style="color: <!--{% if target.certinfo.has_sha1_in_certificate_chain %}-->red<!--{% else %}-->green<!--{% endif %}-->"><!--{{ target.certinfo.has_sha1_in_certificate_chain|yesno:"Yes,No" }}--></span>
<!--{% endnoemptylines %}-->
