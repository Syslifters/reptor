<!--{% load md %}--><!--{% noemptylines %}-->
<!--{% if 'sslv2' in target.protocols %}-->    * <span style="color: red">SSLv2</span><!--{% endif %}-->
<!--{% if 'sslv3' in target.protocols %}-->    * <span style="color: red">SSLv3</span><!--{% endif %}-->
<!--{% if 'tlsv1' in target.protocols %}-->    * <span style="color: amber">TLS 1.0</span><!--{% endif %}-->
<!--{% if 'tlsv1_1' in target.protocols %}-->    * <span style="color: amber">TLS 1.1</span><!--{% endif %}-->
<!--{% if 'tlsv1_2' in target.protocols %}-->    * <span style="color: green">TLS 1.2</span><!--{% endif %}-->
<!--{% if 'tlsv1_3' in target.protocols %}-->    * <span style="color: green">TLS 1.3</span><!--{% endif %}-->
<!--{% endnoemptylines %}-->
