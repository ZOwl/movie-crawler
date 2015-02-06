# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter

def item_type(item):
    return type(item).__name__.replace('Item','').lower()

class CSVPipeline(object):
    SaveTypes = ['movie', 'details']

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)

        return pipeline

    def spider_opened(self, spider):
        start_date = datetime.strftime(spider.start_date, "%Y-%m-%d")
        end_date = datetime.strftime(spider.end_date, "%Y-%m-%d")

        self.files = dict([ (name, open('%s_%s_%s.csv' % (name, start_date, end_date), 'w+b')) for name in self.SaveTypes ])
        self.exporters = dict([ (name, CsvItemExporter(self.files[name])) for name in self.SaveTypes])
        [e.start_exporting() for e in self.exporters.values()]

    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        if spider.name == "moviespider":
            what = item_type(item)
            if what in set(self.SaveTypes):
                self.exporters[what].export_item(item)

        return item

# vi: ft=python:tw=0:ts=4:sw=4

