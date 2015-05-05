#!/bin/bash
export HOME=/home/vagrant
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -a /home/vagrant/icommons_ext_tools -r /home/vagrant/icommons_ext_tools/icommons_ext_tools/requirements/local.txt icommons_ext_tools 
