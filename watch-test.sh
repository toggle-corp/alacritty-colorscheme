#!/usr/bin/env bash
set -euo pipefail


find . |\
    grep -E "(.*\.py)|(.*\.toml)" |\
    entr -s "./test.sh"
