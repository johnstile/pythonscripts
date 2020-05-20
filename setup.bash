#!/bin/bash
#-------------------------------------
echo "[--] Python Virtual Environment"
venv="venv3"
do_install_virtual_environment="y"
if [ -d "$venv" ]; then
 echo "[??] $venv already present. Replace? y/[n]"
 read do_install_virtual_environment
fi
if [ "$do_install_virtual_environment" == "y" ]; then
 TASK="Creating $venv"
 if [ -d "$venv" ]; then
  rm -rf "$venv"
 fi
 echo "[>>] $TASK"
 virtualenv --python=python3 $venv
 if [ $? != 0 ]; then
  echo "[!!] FAIL: $TASK"
  exit 1
 fi
 TASK="Activate virtual environment" 
 echo "[>>] $TASK"
 . $venv/bin/activate
 if [ $? != 0 ]; then
  echo "[!!] FAIL: $TASK"
  exit 1
 fi
 TASK="Install python modules"
 echo "[>>] $TASK" 
 pip3 install -r pip_requirements.txt
 if [ $? != 0 ]; then
  echo "[!!] FAIL: $TASK"
  exit 1
 fi
 TASK="Update everything"
 echo "[>>] $TASK"
 pip install pip-review
 pip-review --auto
 if [ $? != 0 ]; then
  echo "[!!] FAIL: $TASK"
  exit 1
 fi
 echo "[OK] Success Install Python Virtual Environment"
fi
#-------------------------------------
