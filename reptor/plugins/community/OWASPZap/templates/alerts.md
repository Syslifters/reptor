<!--{% load md %}--><!--{% for alert in site.alerts %}-->
*<!--{{alert.name}}-->*

| Target | Information |
| :--- | :--- |
| Risk | <!--{{alert.riskdesc}}--> |
| Confidence | <!--{{alert.confidencedesc}}--> |
| Number of Affected Instances | <!--{{alert.count}}--> |
| CWE | [<!--{{alert.cweid}}-->](https://cwe.mitre.org/data/definitions/<!--{{alert.cweid}}-->.html) |

*Description*

<!--{% autoescape off %}--><!--{{alert.desc}}--><!--{% endautoescape %}-->

*Solution*

<!--{% autoescape off %}--><!--{{alert.solution}}--><!--{% endautoescape %}-->

<!--{% if alert.reference %}-->*References*

<!--{% autoescape off %}--><!--{{reference}}--><!--{% endautoescape %}-->
<!--{% endif %}-->
<!--{% endfor %}-->