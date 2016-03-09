setup()
{
    for func in $SETUP_FUNCTIONS; do
        $func
    done
}

setup
