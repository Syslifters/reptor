<!--{% for nikto_scan in data %}--><!--{% load md %}-->
# Nikto Scan Results

CMD Options: `<!--{{ nikto_scan.options  }}-->`

## Details

| Target | Information |
| :--- | :--- |
| IP | <!--{{ nikto_scan.scandetails.targetip }}--> |
| Port | <!--{{ nikto_scan.scandetails.targetport }}--> |
| Hostname | <!--{{ nikto_scan.scandetails.targethostname }}--> |
| Sitename | <!--{{ nikto_scan.scandetails.sitename }}--> |
| Host Header | <!--{{ nikto_scan.scandetails.hostheader }}--> |
| Errors | <!--{{ nikto_scan.scandetails.errors }}--> |

## Statistics
| Target | Information |
| :--- | :--- |
| Issues Items | <!--{{ nikto_scan.statistics.itemsfound }}--> |
| Duration | <!--{{ nikto_scan.statistics.elapsed }}--> Seconds |
| Total Checks | <!--{{ nikto_scan.statistics.checks }}--> |


## Issues
| Endpoint | Method | Description | References |
| :----- | :--- | :----- | :---- |
<!--{% noemptylines %}-->
<!--{% for item in nikto_scan.scandetails.items %}-->
| <!--{{ item.endpoint }}--> | <!--{{ item.method }}--> | <!--{{ item.description }}--> | <!--{{ item.references }}--> |
<!--{% endfor %}-->
<!--{% endnoemptylines %}-->
<!--{% endfor %}-->