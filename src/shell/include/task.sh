function task()
{
    TASK=$1
    shift

    task-$TASK $*
}

for task_script in $SHELL_DIR/task/*.sh; do
    source $task_script
done
