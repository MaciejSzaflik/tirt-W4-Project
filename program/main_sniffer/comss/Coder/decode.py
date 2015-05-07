#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

def decode(data):
    try:
        #print imgarray[0]
        len1 = int(data[0])
        #print str(len1)
        len2 = int(data[2:(int(data[0]) + 2)])
        #print str(len2) + " \n"
        packetData = data[3 + len1:(3 + len1 + len2)]
        #print packetData
        imgarray = data[(4 + len1 + len2):]
        #print "!!!" + imgarray + "!!!"
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
