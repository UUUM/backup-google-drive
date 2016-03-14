#!/bin/bash
source $(dirname $0)/__init__.sh
$PYTHON $PYTHON_DIR/gdsync/cli/cli.py $@
