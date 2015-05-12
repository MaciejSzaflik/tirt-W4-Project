#!/bin/bash
python streamer_HTTP/StreamerServer.py 6002 &
python streamer_HTTP0/StreamerServer.py 6500 &
python streamer_HTTP1/StreamerServer.py 7000
