{% load l10n %}
{% for target in data %}
# {{ target.hostname }}:{{ target.port|unlocalize }} ({{ target.ip_address }})
**Protocols**

{% if 'sslv2' in target.protocols %}    * <span style="color: red">SSLv2</span>{% endif %}
{% if 'sslv3' in target.protocols %}    * <span style="color: red">SSLv3</span>{% endif %}
{% if 'tlsv1' in target.protocols %}    * <span style="color: red">TLS 1.0</span>{% endif %}
{% if 'tlsv1_1' in target.protocols %}    * <span style="color: red">TLS 1.1</span>{% endif %}
{% if 'tlsv1_2' in target.protocols %}    * <span style="color: red">TLS 1.2</span>{% endif %}
{% if 'tlsv1_3' in target.protocols %}    * <span style="color: red">TLS 1.3</span>{% endif %}

**Certificate Information**

{% if target.certinfo.certificate_untrusted %}
 * <span style="color: red">Certificate untrusted by:</span>{% else %} * <span style="color: green">Certificate is trusted</span>{% endif %}
 * Certificate matches hostname: 
<span style="color: {% if target.certinfo.certificate_matches_hostname %}green{% else %}red{% endif %}">
    {{ target.certinfo.certificate_matches_hostname|yesno:"Yes,No" }}
</span>
 * SHA1 in certificate chain: 
<span style="color: {% if target.certinfo.has_sha1_in_certificate_chain %}red{% else %}green{% endif %}">
    {{ target.certinfo.has_sha1_in_certificate_chain|yesno:"Yes,No" }}
</span>

**Vulnerabilities**

 * Heartbleed: 
<span style="color: {% if target.vulnerabilities.heartbleed %}red{% else %}green{% endif %}">
    {{ target.vulnerabilities.heartbleed|yesno:"Yes,No" }}
</span>
 * Robot Attack: 
<span style="color: {% if target.vulnerabilities.robot %}red{% else %}green{% endif %}">
    {{ target.vulnerabilities.robot|yesno:"Yes,No" }}
</span>
 * OpenSSL CCS (CVE-2014-0224): 
<span style="color: {% if target.vulnerabilities.openssl_ccs %}red{% else %}green{% endif %}">
    {{ target.vulnerabilities.openssl_ccs|yesno:"Yes,No" }}
</span>


**Misconfigurations**

 * Compression: 
<span style="color: {% if target.misconfigurations.compression %}red{% else %}green{% endif %}">
    {{ target.misconfigurations.compression|yesno:"Yes,No" }}
</span>
 * Downgrade Attack (no SCSV fallback): 
<span style="color: {% if target.misconfigurations.downgrade %}red{% else %}green{% endif %}">
    {{ target.misconfigurations.downgrade|yesno:"Yes,No" }}
</span>
 * No Secure Renegotiation: 
<span style="color: {% if target.misconfigurations.no_secure_renegotiation %}red{% else %}green{% endif %}">
    {{ target.misconfigurations.no_secure_renegotiation|yesno:"Yes,No" }}
</span>
 * Client Renegotiation: 
<span style="color: {% if target.misconfigurations.accepts_client_renegotiation %}red{% else %}green{% endif %}">
    {{ target.misconfigurations.accepts_client_renegotiation|yesno:"Yes,No" }}
</span>

**Weak Cipher Suites**
{% if not target.has_weak_ciphers %}
<span style="color: green">No weak ciphers found{% else %}
{% endif %}
{% for cipher in target.protocols.sslv2.insecure_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (SSLv2){% endfor %}
{% for cipher in target.protocols.sslv3.insecure_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (SSLv3){% endfor %}
{% for cipher in target.protocols.tlsv1.insecure_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (TLS 1.0){% endfor %}
{% for cipher in target.protocols.tlsv1_1.insecure_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (TLS 1.1){% endfor %}
{% for cipher in target.protocols.tlsv1_2.insecure_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (TLS 1.2){% endfor %}
{% for cipher in target.protocols.tlsv1_3.insecure_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (TLS 1.3){% endfor %}

{% for cipher in target.protocols.sslv2.weak_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (SSLv2){% endfor %}
{% for cipher in target.protocols.sslv3.weak_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (SSLv3){% endfor %}
{% for cipher in target.protocols.tlsv1.weak_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (TLS 1.0){% endfor %}
{% for cipher in target.protocols.tlsv1_1.weak_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (TLS 1.1){% endfor %}
{% for cipher in target.protocols.tlsv1_2.weak_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (TLS 1.2){% endfor %}
{% for cipher in target.protocols.tlsv1_3.weak_ciphers %}
 * <span style="color: red">{{ cipher }}</span> (TLS 1.3){% endfor %}

{% endfor %}