function git-hook-pre-commit-python-flake8()
{
    git-commited-files | \
        grep '\.py$' | \
        xargs $XARGS_NO_RUN $BIN_DIR/task.sh python-flake8
}
