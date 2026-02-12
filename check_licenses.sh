#!/bin/bash
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately

allow_only="MIT"
allow_only="$allow_only;MIT License"
allow_only="$allow_only;BSD License"
allow_only="$allow_only;BSD-3-Clause"
allow_only="$allow_only;Apache Software License"
allow_only="$allow_only;GNU Library or Lesser General Public License (LGPL)"
allow_only="$allow_only;GNU Lesser General Public License v2 or later (LGPLv2+)"
allow_only="$allow_only;GNU Lesser General Public License v3 (LGPLv3)"
allow_only="$allow_only;GNU Lesser General Public License v3 or later (LGPLv3+)"
allow_only="$allow_only;Mozilla Public License 1.0 (MPL)"
allow_only="$allow_only;Mozilla Public License 1.1 (MPL 1.1)"
allow_only="$allow_only;Mozilla Public License 2.0 (MPL 2.0)"
allow_only="$allow_only;Historical Permission Notice and Disclaimer (HPND)"
allow_only="$allow_only;Python Software Foundation License"

ignore="reptor termcolor typing_extensions attrs urllib3"

pip3 install pip-licenses
pip-licenses --allow-only "$allow_only" --ignore-packages $ignore >/dev/null
