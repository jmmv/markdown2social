#! /bin/sh

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
