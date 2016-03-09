PYTHON_DIR=$SRC_DIR/python

PYTHON="/usr/bin/env python"
PYTHON_OPT=

SETUP_FUNCTIONS="$SETUP_FUNCTIONS python-setup"

python-setup()
{
    export PYTHONPATH=$PYTHON_DIR
    export PYTHONIOENCODING=UTF-8
}

exec-python-script()
{
    local name=$(basename $0)
    $PYTHON $BIN_DIR/${name%%.sh}.py $@
}
