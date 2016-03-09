SETUP_FUNCTIONS="config $SETUP_FUNCTIONS"

config()
{
    if [ -f $CONFIG_DIR/config.sh ]; then
        source $CONFIG_DIR/config.sh
    fi
}
