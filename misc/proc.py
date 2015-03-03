#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

import csv

cities = []
d = {}

with open('cities.csv', 'rb') as f:
    spamreader = csv.reader(f)
    for row in spamreader:
        cities.append(row)

with open('details.csv', 'rb') as f:
    spamreader = csv.reader(f)
    for row in spamreader:
        city = row[7].strip()
        if city == "":
            d[row[4]] = ""

for k,v in d.items():
    city = []
    for c in cities:
        if c[1] in k:
            city.append(c)
    city_name = ""
    city_id = ""
    city_len = len(city)
    for i in range(city_len):
        if i > 0:
            city_name += "/"
            city_id += "/"
        city_name += city[i][1]
        city_id += city[i][0]

    d[k] = (city_id, city_name)

    if city_name=="":
        print "insert into theaters (name, city_id) values ('%s', %s);" % (k, city_id)
        continue

    if city_len > 1:
        print "insert into theaters (name, city_id) values ('%s', %s);%s" % (k, city_id, city_name)
    else:
        print "insert into theaters (name, city_id) values ('%s', %s);" % (k, city_id)

# vi: ft=python:tw=0:ts=4:sw=4

