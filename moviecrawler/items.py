# -*- coding: utf-8 -*-

from scrapy.item import BaseItem, Item, Field
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates, relationship

AlchemyBase = declarative_base()

class PrintableItem(BaseItem):
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        colnames = (col.name for col in self.__table__.columns)
        res = []
        for item in ((col, getattr(self, col)) for col in colnames):
            res.append("%s=%s" % item)
        return "<%s %s>" % (self.__class__.__name__, ", ".join(res))

class MovieItem(Item):
    mid = Field()
    date = Field()
    source = Field()
    name = Field()
    box_office = Field()
    daily_box_office = Field()
    valid_sessions = Field()
    invalid_sessions = Field()
    mantime = Field()
    attendance = Field()

class PrintableItem(BaseItem):
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        colnames = (col.name for col in self.__table__.columns)
        res = []
        for item in ((col, getattr(self, col)) for col in colnames):
            res.append("%s=%s" % item)
        return "<%s %s>" % (self.__class__.__name__, ", ".join(res))

class DetailsItem(Item):
    mid = Field()
    source = Field()
    city_name = Field()
    cinema_name = Field()
    time = Field()
    price = Field()
    seating = Field()
    attendance = Field()

class PPItem(PrintableItem, AlchemyBase):
    __tablename__ = 'pps'

    mid = Column(Integer, primary_key=True)

class Schedule(PrintableItem, AlchemyBase):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey('films.id'))
    theater_id = Column(Integer, ForeignKey('theaters.id'))

class Film(PrintableItem, AlchemyBase):
    __tablename__ = 'films'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    released = Column(Date)
    region = Column(String)

class City(PrintableItem, AlchemyBase):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    Index('city_name', 'name', unique=True)

class Theater(PrintableItem, AlchemyBase):
    __tablename__ = 'theaters'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'))

    Index('theater_name', 'name', unique=True)

# vi: ft=python:tw=0:ts=4:sw=4

