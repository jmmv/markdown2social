#! /bin/sh
# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.

set -e -x

python setup.py sdist || exit 1
tgz="$(cd dist && echo *.tar.gz)"
name="$(echo "${tgz}" | sed -e 's/.tar.gz$//')"

rm -rf distcheck
mkdir distcheck
trap "rm -rf '$(pwd)/distcheck'" EXIT
cd distcheck || exit 1

tar xzvf "../dist/${tgz}" || exit 1
cd "${name}" || exit 1

for file in INSTALL.md LICENSE README.md; do
    if [ ! -f "${file}" ]; then
        echo "Expected file in sdist not found: ${file}" 1>&2
        exit 1
    fi
done

python setup.py build || exit 1
python setup.py test || exit 1

if [ "${TRAVIS}" = true ]; then
    python setup.py install || exit 1
else
    prefix="$(cd .. && pwd)/local"
    py_version="$(python -c 'import sys; print "%d.%d" % (
        sys.version_info.major, sys.version_info.minor)')"
    py_dir="${prefix}/lib/python${py_version}/site-packages"
    mkdir -p "${py_dir}"
    PYTHONPATH="${py_dir}" python setup.py install --prefix="${prefix}" \
        || exit 1
fi
