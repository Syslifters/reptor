| Title | Severity | Affected Components |
| ------- | ------- | ------- |
<!--{% for f in findings %}--><!--{% load md %}--><!--{% oneliner %}-->
| <!--{{f.name}}-->
| <!--{{f.severity|title}}-->
| <!--{% if f.affected_components|length > 0 %}--><ul>
<!--{% for a in f.affected_components %}--><li><!--{{a}}--></li><!--{% endfor %}-->
</ul><!--{% endif %}--> |
<!--{% endoneliner %}-->
<!--{% endfor %}-->