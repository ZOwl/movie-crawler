# -*- coding: utf-8 -*-

"""

"""

import re
import random
import itertools
import time

from datetime import datetime, date, timedelta
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.item import Item
from scrapy.http import FormRequest,Request
from scrapy import log
from scrapy.conf import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from moviecrawler.items import MovieItem, DetailsItem, PPItem, Film, City, Theater, AlchemyBase

SOURCES = {
    "wangpiao": u"网票",
    "hipiao": u"哈票",
    # "gewara": u"格瓦拉",
    "wanda": u"万达",
    "jinyi": u"金逸",
    "tpiao": u"淘电影"
    }

SITE = "http://58921.com"
PP_SITE = "http://pp.58921.com"

class MovieSpider(Spider):
    name = 'moviespider'
    sid = ''
    papers = []
    start_urls = ["%s/user/login" % SITE]

    def __init__(self, start=None, end=None, only_film=None, get_schedules=None, *args, **kwargs):
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


        self.only_film_flag = only_film
        self.get_schedules_flag = get_schedules

        engine = create_engine(settings['SQLALCHEMY_ENGINE_URL'])
        self.session = scoped_session(sessionmaker(engine))()

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
                    url = "%s/boxoffice/%s/%s/" % (SITE, k, datetime.strftime(d, "%Y%m%d"))
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
            mantime_extracted = lst[5].xpath("a/text()").extract()
            if mantime_extracted: mantime=mantime_extracted[0]
            details = lst[7].xpath("a[@title='%s']/@href" % u"明细")

            yield Request(url="%s/film/%s" % (SITE, mid), callback=lambda r, m=mid: self.get_film(r, m))

            if not self.only_film_flag:
                yield MovieItem(
                        mid=mid,
                        date=cdate,
                        source=source,
                        name=name,
                        box_office=box_office,
                        invalid_sessions=invalid_sessions,
                        mantime=mantime
                        )
                start = int(time.mktime(time.strptime(cdate, "%Y-%m-%d")))
                yield Request(url="%s%s" % (SITE, details.extract()[0]), callback=lambda r,tr=(start, 86400): self.get_details_by_time_range(r,tr))

            if self.get_schedules_flag:
                yield Request(url="%s/film/%s" % (PP_SITE, mid), callback=lambda r, d=cdate: self.get_pp(r, d))

    def get_film(self, response, mid):
        sel = response.selector
        name_item = sel.xpath("//div[@id='main']//div[@class='page-header']//h1/text()")
        name = name_item[0].extract().strip()

        other_items = sel.xpath("//div[@class='media-body']//ul//li")

        box_office = current_box_office = directors = writers = stars = released = length = production_regions = types = languages = companies = None

        for item in other_items:
            try:
                if item.extract().find(u"<strong>总票房：</strong>") != -1:
                    box_office = item.xpath("a/text()").extract()[0].strip()
                    if not box_office[-3].isdigit(): box_office = None
                if item.extract().find(u"<strong>实时票房：</strong>") != -1:
                    current_box_office = item.xpath("a/text()").extract()[0].strip()
                if item.extract().find(u"<strong>导演：</strong>") != -1:
                    directors = " ".join(item.xpath("a/text()").extract())
                if item.extract().find(u"<strong>编剧：</strong>") != -1:
                    writers = " ".join(item.xpath("a/text()").extract())
                if item.extract().find(u"<strong>主演：</strong>") != -1:
                    stars = " ".join(item.xpath("a/text()").extract())
                if item.extract().find(u"<strong>上映时间：</strong>") != -1:
                    released = item.xpath("text()").extract()[0]
                if item.extract().find(u"<strong>片长：</strong>") != -1:
                    length = item.xpath("text()").extract()[0]
                if item.extract().find(u"<strong>制作国家/地区：</strong>") != -1:
                    production_regions  = " ".join(item.xpath("a/text()").extract())
                if item.extract().find(u"<strong>类型：</strong>") != -1:
                    types = " ".join(item.xpath("a/text()").extract())
                if item.extract().find(u"<strong>语言：</strong>") != -1:
                    languages = " ".join(item.xpath("a/text()").extract())
                if item.extract().find(u"<strong>发行制作公司：</strong>") != -1:
                    companies = " ".join(item.xpath("a/text()").extract())
            except Exception as e:
                pass

        yield Film(
                id=int(mid),
                name=name,
                box_office=box_office,
                current_box_office=current_box_office,
                directors=directors,
                writers=writers,
                stars=stars,
                released=released,
                length=length,
                production_regions=production_regions,
                types=types,
                languages=languages,
                companies=companies
                )

    def get_pp(self, response, cdate):
        sel = response.selector
        cities = sel.xpath("//table[@class='table table-bordered table-condensed']//thead//tr//th//a")
        other_cities=sel.xpath("//div[@id='2']//li//a")
        # pp_dates = sel.xpath("//div[@id='content']//li//a/text()").re(r'.+\d+')

        for city in itertools.chain(cities, other_cities):
            name = city.xpath("text()").extract()[0].split(" ")[0]
            link = city.xpath("@href").extract()[0]

            yield City(name=name)
            city = self.session.query(City).filter_by(name=name).first()
            yield Request(url="%s%s/%s" % (PP_SITE, link, cdate.replace("-", "")), callback=lambda r,cid=city.id: self.get_pp_details(r, cid))

    def get_pp_details(self, response, city_id):
        sel = response.selector
        theaters=sel.xpath("//table[@class='table table-bordered table-condensed']//tbody//tr//td//a/text()")

        for theater in theaters:
            yield Theater(name=theater.extract(), city_id=city_id)

    def get_details(self, response):
        items = response.selector.xpath("//div[@class='movie_block_schedule_query']//a[contains(@href, '?cid=')]")
        for item in items:
            city_name = item.xpath("text()").extract()[0]
            uri = item.xpath("@href").extract()[0]
            yield Request(url="%s%s" % (SITE, uri), callback=lambda r,cn=city_name: self.get_details_by_city(r,cn))

    def get_details_by_time_range(self, response, time_range, sorted_flag=None):
        start, step = time_range
        sel = response.selector

        pager_item = sel.xpath("//ul[@class='pager']")
        pager_number_item = pager_item.xpath("li[@class='pager_count']//span[@class='pager_number']/text()").extract()
        end = start + step
        missing = None

        if pager_number_item:
            pager_number = int(pager_number_item[0].split("/")[1])
            if pager_number > 10:
                if sorted_flag: missing = True
                url_prefix = response.url.rsplit("?", 1)[0]
                if step > 1:
                    new_step = step/2
                    median = start + new_step
                    yield Request(url="%s?start=%s&end=%s" % (url_prefix, start, median), callback=lambda r,tr=(start, new_step): self.get_details_by_time_range(r,tr))
                    yield Request(url="%s?start=%s&end=%s" % (url_prefix, median, end), callback=lambda r,tr=(median, new_step): self.get_details_by_time_range(r,tr))

                    return
                elif step == 1 and not sorted_flag:
                    yield Request(url=u"%s?sort=desc&order=影院名称&start=%s&end=%s" % (url_prefix, start, step), callback=lambda r,tr=(start, step),sf=True: self.get_details_by_time_range(r,tr,sorted_flag=sf))
                    yield Request(url=u"%s?sort=asc&order=影院名称&start=%s&end=%s" % (url_prefix, start, step), callback=lambda r,tr=(median, step),sf=True: self.get_details_by_time_range(r,tr,sorted_flag=sf))
            else:
                next_page = pager_item.xpath("li[@class='pager_next']//a/@href").extract()
                if(next_page):
                    yield Request(url="%s%s" % (SITE, next_page[0]), callback=lambda r,tr=time_range: self.get_details_by_time_range(r,tr))

        items = sel.xpath("//table[@class='center_table table table-bordered table-condensed']//tbody//tr")
        s = response.url[30:] # FIXME(ZOwl): using magic number, need refactoring
        m = re.match(r'(\d+)/schedule/(\w+)/.*', s)

        for item in items:
            temp_records = item.xpath("td/text()")
            attendance = temp_records[4].extract()
            if(attendance == u"请登录"):
                yield Request(url=self.start_urls[0], callback=lambda r,f=True: self.login(r, isRelogin=f), dont_filter=True)
                yield Request(url=response.url, callback=lambda r,tr=time_range: self.get_details_by_time_range(r,tr))
                return

            cinema_name=temp_records[0].extract()
            theater = self.session.query(Theater).filter_by(name=unicode(cinema_name)).first()
            city_name = None
            if theater:
                city = self.session.query(City).filter_by(id=theater.city_id).first()
                if city:
                    city_name=city.name

            yield DetailsItem(mid=m.group(1),
                    source=SOURCES[m.group(2)],
                    city_name=city_name,
                    cinema_name=cinema_name,
                    time=temp_records[1].extract(),
                    price=temp_records[2].extract(),
                    seating=temp_records[3].extract(),
                    attendance=attendance,
                    missing=missing)

    def get_details_by_city(self, response, city_name):
        items = response.selector.xpath("//table[@class='center_table table table-bordered table-condensed']//tbody//tr")
        s = response.url[30:] # FIXME(ZOwl): using magic number, need refactoring
        m = re.match(r'(\d+)/schedule/(\w+)/.*', s)

        for item in items:
            temp_records = item.xpath("td/text()")
            attendance = temp_records[4].extract()
            if(attendance == u"请登录"):
                yield Request(url=self.start_urls[0], callback=lambda r,f=True: self.login(r, isRelogin=f), dont_filter=True)
                yield Request(url=response.url, callback=lambda r,cn=city_name: self.get_details_by_city(r,cn), dont_filter=True)
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
            yield Request(url="%s%s" % (SITE, next_page.extract()), callback=self.get_details_by_city)

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
