<!--{% load md %}--><!--{% noemptylines %}-->
<!--{% if not has_weak_ciphers and not has_insecure_ciphers %}-->
<span style="color: green">No weak ciphers found<!--{% else %}-->
<!--{% endif %}-->
<!--{% for cipher in protocols.sslv2.insecure_ciphers %}-->
 * <span style="color: red"><!--{{ cipher }}--></span> (SSLv2)<!--{% endfor %}-->
<!--{% for cipher in protocols.sslv3.insecure_ciphers %}-->
 * <span style="color: red"><!--{{ cipher }}--></span> (SSLv3)<!--{% endfor %}-->
<!--{% for cipher in protocols.tlsv1.insecure_ciphers %}-->
 * <span style="color: red"><!--{{ cipher }}--></span> (TLS 1.0)<!--{% endfor %}-->
<!--{% for cipher in protocols.tlsv1_1.insecure_ciphers %}-->
 * <span style="color: red"><!--{{ cipher }}--></span> (TLS 1.1)<!--{% endfor %}-->
<!--{% for cipher in protocols.tlsv1_2.insecure_ciphers %}-->
 * <span style="color: red"><!--{{ cipher }}--></span> (TLS 1.2)<!--{% endfor %}-->
<!--{% for cipher in protocols.tlsv1_3.insecure_ciphers %}-->
 * <span style="color: red"><!--{{ cipher }}--></span> (TLS 1.3)<!--{% endfor %}-->

<!--{% for cipher in protocols.sslv2.weak_ciphers %}-->
 * <span style="color: orange"><!--{{ cipher }}--></span> (SSLv2)<!--{% endfor %}-->
<!--{% for cipher in protocols.sslv3.weak_ciphers %}-->
 * <span style="color: orange"><!--{{ cipher }}--></span> (SSLv3)<!--{% endfor %}-->
<!--{% for cipher in protocols.tlsv1.weak_ciphers %}-->
 * <span style="color: orange"><!--{{ cipher }}--></span> (TLS 1.0)<!--{% endfor %}-->
<!--{% for cipher in protocols.tlsv1_1.weak_ciphers %}-->
 * <span style="color: orange"><!--{{ cipher }}--></span> (TLS 1.1)<!--{% endfor %}-->
<!--{% for cipher in protocols.tlsv1_2.weak_ciphers %}-->
 * <span style="color: orange"><!--{{ cipher }}--></span> (TLS 1.2)<!--{% endfor %}-->
<!--{% for cipher in protocols.tlsv1_3.weak_ciphers %}-->
 * <span style="color: orange"><!--{{ cipher }}--></span> (TLS 1.3)<!--{% endfor %}-->
<!--{% endnoemptylines %}-->
