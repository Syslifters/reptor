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