#!/bin/bash


APP_PATH=$HOME/workspaces/realadvisor

cd $APP_PATH
source $APP_PATH/.venv/bin/activate
$APP_PATH/.venv/bin/python $APP_PATH/src/daemon.py --config local/realadvisor_conf.yaml --log-config local/logging.conf --start 