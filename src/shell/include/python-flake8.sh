function python-flake8()
{
    if [ -z "$*" ]; then
        flake8 $PYTHON_DIR
    else
        flake8 $*
    fi
}
