#!/bin/bash
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately

allow_only="MIT"
allow_only="$allow_only;MIT License"
allow_only="$allow_only;BSD License"
allow_only="$allow_only;Apache Software License"
allow_only="$allow_only;GNU Library or Lesser General Public License (LGPL)"
allow_only="$allow_only;GNU Lesser General Public License v2 or later (LGPLv2+)"
allow_only="$allow_only;GNU Lesser General Public License v3 (LGPLv3)"
allow_only="$allow_only;Mozilla Public License 1.0 (MPL)"
allow_only="$allow_only;Mozilla Public License 1.1 (MPL 1.1)"
allow_only="$allow_only;Mozilla Public License 2.0 (MPL 2.0)"
allow_only="$allow_only;Historical Permission Notice and Disclaimer (HPND)"
allow_only="$allow_only;Python Software Foundation License"

ignore="reptor"

pip3 install pip-licenses
pip-licenses --allow-only "$allow_only" >/dev/null
pip-licenses -l --no-license-path -f plain-vertical --no-version --ignore-packages $ignore > NOTICE

cme_license='''crackmapexec
Copyright (c) 2022, byt3bl33d3r, mpgn_x64
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

echo "$cme_license" >> NOTICE