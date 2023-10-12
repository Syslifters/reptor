<!--{% if has_cert_issues %}--><!--{% load md %}--><!--{% oneliner %}-->
The certificates of <!--{{ affected_components_short|first }}-->
<!--{% if affected_components_short|length == 2 %}-->
and <!--{{ affected_components_short|last }}-->
<!--{% elif affected_components_short|length > 2 %}-->
and <!--{{ affected_components_short|length|add:"-1"|safe }}--> other services
<!--{% endif %}-->
are untrusted by common browsers:
<!--{% endoneliner %}-->

<!--{% noemptylines %}-->
<!--{% for t in data %}-->
<!--{% if t.has_cert_issues %}-->
<!--{% oneliner %}-->
* <!--{{ t.hostname }}-->:<!--{{ t.port }}-->
<!--{% if t.certinfo.certificate_untrusted and not t.certinfo.certificate_matches_hostname %}-->
(unmatching hostname, untrusted by <!--{{ t.certinfo.certificate_untrusted|join:", " }}-->)
<!--{% elif t.certinfo.certificate_untrusted %}-->
(untrusted by <!--{{ t.certinfo.certificate_untrusted|join:", " }}-->)
<!--{% elif not t.certinfo.certificate_matches_hostname %}-->
(unmatching hostname)
<!--{% endif %}-->
<!--{% endoneliner %}-->
<!--{% endif %}-->
<!--{% endfor %}-->
<!--{% endnoemptylines %}-->
<!--{% endif %}-->