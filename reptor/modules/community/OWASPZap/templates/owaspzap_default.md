{% for site in data %}
# OWASPZap Scan

## Site Details
| Target | Information |
| :--- | :--- |
| Site | {{site.name}} |
| Host | {{site.host}} |
| Port | {{site.port}} |
| SSL ? | {% if site.ssl %} Yes {% else %} No {% endif %} |

## Alerts

    {% for alert in site.alerts %}
        ### {alert.name}
        | Target | Information |
        | :--- | :--- |
        | Risk | {{alert.riskdesc}} |
        | Confidence | {{alert.confidencedesc}} |
        | Number of Affected Instances | {{alert.count}} |
        | CWE | [{{alert.cweid}}](https://cwe.mitre.org/data/definitions/{{alert.cweid}}.html) |

        ### Description
        {{alert.desc}}

        ### Solution
        {{alert.solution}}

        ### References
        {% if alert.reference %}
            {% for reference in alert.references_as_list_items %}
            - [{{reference}}]({{reference}})
            {% endfor %}
        {% else %}
            None
        {% endif %}

    {% endfor %}
{% endfor %}