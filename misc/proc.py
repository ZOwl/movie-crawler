#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

import csv
import sys

sys.path.append("..")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from moviecrawler.items import Film, City, Theater

cities = []
d = {}

engine = create_engine("sqlite:///../moviecrawler/scraping.db")
session = scoped_session(sessionmaker(engine))()

key_words = [
            u"大地影院", u"大地影城",
            u"大地国际影院", u"大地国际影城",
            u"17.5影院", u"17.5影城",
            u"17.5国际影院", u"17.5国际影城",
            u"星美影院", u"星美影城",
            u"星美国际影院", u"星美国际影城",
            u"电影院", u"电影城",
            u"影院", u"影城",
            u"中影",
            u"（", u"）",
            u"(", u")",
            u"店"
            ]

with open('cities.csv', 'rb') as f:
    spamreader = csv.reader(f)
    for row in spamreader:
        cities.append(row)

with open('details.csv', 'rb') as f:
    spamreader = csv.reader(f)
    for row in spamreader:
        city = row[8].strip()
        if city == "":
            d[row[5]] = ""

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
        name = k.decode("utf-8")
        for w in key_words:
            name = name.replace(w, u"")
        theaters = session.query(Theater).filter(Theater.name.like("%"+name+"%"))

        theater_names = []
        city_names = []
        city_ids = []
        for t in theaters:
            cid = str(t.city_id)
            if not cid in city_ids:
                city_ids.append(cid)
                city = session.query(City).filter_by(id=cid).first()
                city_names.append(city.name)
        if len(city_ids) > 1:
            print "insert into theaters (name, city_id) values ('%s', %s);%s" % (k.decode("utf-8"), "/".join(city_ids), "/".join(city_names))
        elif len(city_ids) == 1:
            print "insert into theaters (name, city_id) values ('%s', %s);" % (k.decode("utf-8"), city_ids[0])
        continue

    if city_len > 1:
        print "insert into theaters (name, city_id) values ('%s', %s);%s" % (k, city_id, city_name)
    else:
        print "insert into theaters (name, city_id) values ('%s', %s);" % (k, city_id)

# vi: ft=python:tw=0:ts=4:sw=4

