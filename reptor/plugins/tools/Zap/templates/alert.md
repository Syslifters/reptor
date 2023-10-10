<!--{% load md %}-->
| Target | Information |
| :--- | :--- |
| Risk | <!--{{riskdesc}}--> |
| Number of Affected Instances | <!--{{count}}--> |
| CWE | [<!--{{cweid}}-->](https://cwe.mitre.org/data/definitions/<!--{{cweid}}-->.html) |

**Instances**
<!--{% load md %}--><!--{% noemptylines %}-->
| Method | URI | Param | Payload |
| :--- | :--- | :--- | :--- |
<!--{% for instance in instances %}-->
| <!--{{instance.method}}--> | <!--{{instance.uri}}--> | <!--{{instance.param}}--> | <!--{{instance.attack}}--> |
<!--{% endfor %}-->
<!--{% endnoemptylines %}-->

**Description**

<!--{% autoescape off %}--><!--{{desc}}--><!--{% endautoescape %}-->

**Solution**

<!--{% autoescape off %}--><!--{{solution}}--><!--{% endautoescape %}-->

<!--{% if reference %}-->**References**

<!--{% autoescape off %}--><!--{{reference}}--><!--{% endautoescape %}-->
<!--{% endif %}-->