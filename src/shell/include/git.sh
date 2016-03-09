function git-commited-files()
{
    git diff --cached --name-only --diff-filter=ACMR
}

function git-hook()
{
    declare -F | grep git-hook-$1 | awk '{print $3}' | while read func; do
        $func
        ret=$?
        if [ $ret -ne 0 ]; then
            exit $ret
        fi
    done
}

function git-hook-register()
{(
    cd $TOP_DIR
    find .git_template -type f | while read src_file; do
        dest_file=${src_file/.git_template/.git}
        if [ -f $dest_file ]; then
            continue
        fi

        src_dir=
        dir=$(dirname $src_file)
        while [ $dir != '.' ]; do
            dir=$(dirname $dir)
            src_dir=../$src_dir
        done

        mkdir -p $(dirname $dest_file)
        ln -s $src_dir$src_file $dest_file
    done
)}

for hook_script in $SHELL_DIR/git-hook/*.sh; do
    source $hook_script
done
