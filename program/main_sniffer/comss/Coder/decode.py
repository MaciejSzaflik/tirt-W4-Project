#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

def decode(data):
    try:
        len1 = int(data[0])
        len2 = int(data[2:(int(data[0]) + 2)])
        packetData = data[3 + len1:(3 + len1 + len2)]
        imgarray = data[(4 + len1 + len2):]
        try:
            packetData = json.loads(packetData)

            return {
                'data': packetData,
                'body': imgarray
            }

        except Exception, e:
            pass
    except:
        pass

    return None
