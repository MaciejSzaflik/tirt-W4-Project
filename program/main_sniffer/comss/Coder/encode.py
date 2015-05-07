#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

def encode(jsonObject, restOfData):
    data = json.dumps(jsonObject)
    #print str(len(str(len(data)))) + "_" + str(len(data)) + "_" + data
    return str(len(str(len(data)))) + "_" + str(len(data)) + "_" + data + "_" + restOfData

