# -*- coding: utf-8 -*-

"""

"""

import re
import random

from datetime import datetime, date, timedelta
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.item import Item
from scrapy.http import FormRequest,Request
from scrapy import log

from moviecrawler.items import MovieItem, DetailsItem

SOURCES = {
    "wangpiao": u"网票",
    "hipiao": u"哈票",
    # "gewara": u"格瓦拉",
    "wanda": u"万达",
    "jinyi": u"金逸",
    "tpiao": u"淘电影"
    }
HOST = "http://58921.com"

class MovieSpider(Spider):
    name = 'moviespider'
    sid = ''
    papers = []
    start_urls = ["%s/user/login" % HOST]

    def __init__(self, start=None, end=None, *args, **kwargs):
        # LOG_FILE = "scrapy_%s_%s.log" % (self.name, datetime.now())
        # remove the current log
        # log.log.removeObserver(log.log.theLogPublisher.observers[0])
        # re-create the default Twisted observer which Scrapy checks
        # log.log.defaultObserver = log.log.DefaultObserver()
        # start the default observer so it can be stopped
        # log.log.defaultObserver.start()
        # trick Scrapy into thinking logging has not started
        # log.started = False
        # start the new log file observer
        # log.start(LOG_FILE)
        # continue with the normal spider init

        super(MovieSpider, self).__init__(*args, **kwargs)

        if start and end:
            self.start_date = datetime.strptime(start, "%Y-%m-%d")
            self.end_date = datetime.strptime(end, "%Y-%m-%d")
            if self.end_date < self.start_date:
                print "ERROR: end date must later than start date."
                return
            today = datetime.utcnow().date()
            begin_of_today = datetime(today.year, today.month, today.day)
            if self.end_date >= begin_of_today:
                self.end_date = today - timedelta(1)
        else:
            print "USAGE: scrapy crawler moviespider -a start='[yyyy-mm-dd]' -a end='[yyyy-mm-dd]'"
            return

    def parse(self, response):
        return self.login(response);

    def after_login(self, response, isRelogin):
        # check login succeed before going on
        if "authentication failed" in response.body:
            # self.log("Login failed", level=log.ERROR)
            print "Login failed"
            return

        if not isRelogin:
            for k, v in SOURCES.items():
                for n in range(int ((self.end_date - self.start_date).days) + 1):
                    d = self.start_date + timedelta(n)
                    url = "%s/boxoffice/%s/%s/" % (HOST, k, datetime.strftime(d, "%Y%m%d"))
                    yield Request(url=url, callback=lambda r, f=datetime.strftime(d, "%Y-%m-%d"), s=v: self.get_daily_box_office(r, f, s))

    def get_daily_box_office(self, response, cdate, source):
        items = response.selector.xpath("//div[@class='box_office_type_view']//tr[@class!='box_office_view_table_name']")
        # d = date.strftime(datetime.strptime(response.url[-9:-1], "%Y%m%d"), "%Y-%m-%d")
        for item in items:
            lst = item.xpath("td")
            mid = lst[0].xpath("a/@href").extract()[0][6:].split("/")[0]
            name = lst[0].xpath("a/text()").extract()[0]
            box_office = lst[1].xpath("a/text()").extract()[0]
            invalid_sessions = lst[4].xpath("text()").extract()[0]
            mantime = lst[5].xpath("a/text()").extract()[0]
            details = lst[7].xpath("a[@title='%s']/@href" % u"明细")
            yield MovieItem(
                    mid=mid,
                    date=cdate,
                    source=source,
                    name=name,
                    box_office=box_office,
                    invalid_sessions=invalid_sessions,
                    mantime=mantime
                    )
            yield Request(url="%s%s" % (HOST, details.extract()[0]), callback=self.get_details)

    def get_schedule(self, response):
        pass

    def get_details(self, response):
        items = response.selector.xpath("//div[@class='movie_block_schedule_query']//a[contains(@href, '?cid=')]")
        for item in items:
            city_name = item.xpath("text()").extract()[0]
            uri = item.xpath("@href").extract()[0]
            yield Request(url="%s%s" % (HOST, uri), callback=lambda r,cn=city_name: self.get_details_by_city(r,cn))

    def get_details_by_city(self, response, city_name):
        items = response.selector.xpath("//table[@class='center_table table table-bordered table-condensed']//tbody//tr")
        s = response.url[30:] # FIXME(ZOwl): using magic number, need refactoring
        m = re.match(r'(\d+)/schedule/(\w+)/.*', s)

        for item in items:
            temp_records = item.xpath("td/text()")
            attendance = temp_records[4].extract()
            if(attendance == u"请登录"):
                yield Request(url=self.start_urls[0], callback=lambda r,f=True: self.login(r, isRelogin=f))
                yield Request(url=response.url, callback=lambda r,cn=city_name: self.get_details_by_city(r,cn))
                return

            yield DetailsItem(mid=m.group(1),
                    source=SOURCES[m.group(2)],
                    city_name=city_name,
                    cinema_name=temp_records[0].extract(),
                    time=temp_records[1].extract(),
                    price=temp_records[2].extract(),
                    seating=temp_records[3].extract(),
                    attendance=attendance)

        next_page = response.selector.xpath("//div[@class='item-list item_pager']//ul[@class='pager']//li[@class='pager_next']//a/@href")
        if(next_page):
            yield Request(url="%s%s" % (HOST, next_page.extract()), callback=self.get_details_by_city)

    def login(self, response, isRelogin=False):
        formdata = [
                {'mail': 'jacky_luo_1984@163.com', 'pass': 'piaofang123'},
                {'mail': 'luozijun.cn@gmail.com', 'pass': 'piaofang123'},
                {'mail': 'jacky_luo_1984@hotmail.com', 'pass': 'piaofang123'},
                {'mail': 'luozijun@ksu.edu', 'pass': 'piaofang123'},
                {'mail': 'jacky_luo_1984@sina.com', 'pass': 'piaofang123'},
                {'mail': 'jacky_luo_1984@sogou.com', 'pass': 'piaofang123'},
                {'mail': '82127512@qq.com', 'pass': 'piaofang123'}
                ][random.randrange(0,7,1)]

        print formdata
        return FormRequest.from_response(
            response,
            formdata=formdata,
            callback=lambda r, i=isRelogin: self.after_login(r, i)
        )

# vi: ft=python:tw=0:ts=4:sw=4
