# Upcoming
* Implement Qualys importer
* Fix incompatible field types from variables (#173)

# 0.29
* Allow finish and reactivate projects
* Remove wrong timestamps for project sections
* Improve setting config, mark project ID as optional
* Fix linting and problems

# 0.28
* Use pagination for projects, templates and designs
* Deprecate "get_template_overview" in TemplatesAPI
* Deprecate "get_projects" in ProjectsAPI
* Allow deleting projects by ID
* Minor code cleanup

# 0.27
* Fix error when exporting finding field "id"

# 0.26
* Fix errors for cvss "None"

# 0.25
* Improvements in reptor packarchive
* add Nessus "snoozed" filter (credits to emizzz)

# 0.24
* Introduce support for CVSS4

# 0.23
* Fix error for rendering with alternative design

# 0.22
* Update reptor for updated SysReptor field definition
* Raise error if wrong server URL was specified

# 0.21
* Create findings from finding templates
* Fix errors in exportfindings plugin
* Error message if no SysReptor server specified

# 0.20
* Introduce Burp plugin
* Add aliases for options

# 0.19
* Update docs and CI

# 0.18
* Several adaptions to allow reptor be used as library

# 0.17
* Respect finding order in Project (and exportfindings)

# 0.16
* Remove locking
* Strip bogus API token prefix if http header is provided
* Fix Nessus affected_components aggregation error
* Don't skip findings created from templates
* Don't through error if plugin source directory doesn't exists when copy

# 0.15
skipped

# 0.14
* Allow multiple inputs via -i switch
* Fix bug in Nessus and OpenVAS plugins
* Deprecate Locking of notes for upcoming SysReptor release
* Provide reptorlib for library usage
* Implement plugin for deleting projects
* Allow configuration from env variables