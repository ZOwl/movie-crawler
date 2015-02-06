# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

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

class DetailsItem(Item):
    mid = Field()
    source = Field()
    cinema_name = Field()
    time = Field()
    price = Field()
    seating = Field()
    attendance = Field()

# vi: ft=python:tw=0:ts=4:sw=4

