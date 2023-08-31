# ZAP Module

The module supports XML and JSON Input from ZAP Scanner Results Reports.

In ZAP click on `Report` -> `Generate Report`.

In the Popup click on the tab `Template` and choose one of the following:

- Traditional XML Report
- Traditional XML Report with Requests and Responses
- Traditional JSON Report
- Traditional JSON Report with Requests and Responses

>Note: Consider using the filter option to reduce the output to only include High & Medium risks


# Unit Tests

```
python -m unittest discover -v -s modules
```