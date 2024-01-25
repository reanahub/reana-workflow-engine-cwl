#!/usr/bin/env bash
#
# This file is part of REANA.
# Copyright (C) 2017, 2018, 2019, 2020, 2023, 2024 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

set -o errexit
set -o nounset

check_commitlint () {
    from=${2:-master}
    to=${3:-HEAD}
    npx commitlint --from="$from" --to="$to"
    found=0
    while IFS= read -r line; do
        if echo "$line" | grep -qP "\(\#[0-9]+\)$"; then
            true
        else
            echo "✖   PR number missing in $line"
            found=1
        fi
    done < <(git log "$from..$to" --format="%s")
    if [ $found -gt 0 ]; then
        exit 1
    fi
}

check_shellcheck () {
    find . -name "*.sh" -exec shellcheck {} \+
}

check_pydocstyle () {
    pydocstyle reana_workflow_engine_cwl
}

check_black () {
    black --check .
}

check_flake8 () {
    flake8 .
}

check_manifest () {
    check-manifest
}

check_sphinx () {
    sphinx-build -qnNW docs docs/_build/html
}

check_pytest () {
    python setup.py test
}

check_dockerfile () {
    docker run -i --rm docker.io/hadolint/hadolint:v2.12.0 < Dockerfile
}

check_docker_build () {
    docker build -t docker.io/reanahub/reana-workflow-engine-cwl .
}

check_all () {
    check_commitlint
    check_shellcheck
    check_pydocstyle
    check_black
    check_flake8
    check_manifest
    check_sphinx
    check_pytest
    check_dockerfile
    check_docker_build
}

if [ $# -eq 0 ]; then
    check_all
    exit 0
fi

arg="$1"
case $arg in
    --check-commitlint) check_commitlint "$@";;
    --check-shellcheck) check_shellcheck;;
    --check-pydocstyle) check_pydocstyle;;
    --check-black) check_black;;
    --check-flake8) check_flake8;;
    --check-manifest) check_manifest;;
    --check-sphinx) check_sphinx;;
    --check-pytest) check_pytest;;
    --check-dockerfile) check_dockerfile;;
    --check-docker-build) check_docker_build;;
    *) echo "[ERROR] Invalid argument '$arg'. Exiting." && exit 1;;
esac
