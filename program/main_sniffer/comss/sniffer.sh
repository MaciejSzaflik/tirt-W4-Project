#!/bin/bash
sudo python ./gui_service.py &
sudo python ./dataManager_service.py &
sudo python ./videoEffects_service.py &
sudo python ./videoChecker_service.py &
sudo python ./wire_service.py
