#!/bin/bash
sudo tcpdump -i lo -s 65535 -w file.cap && foremost -v -i file.cap -T
