# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
import pymongo
from scrapy.conf import settings

class DuplicatesPipeline(object):

    def __init__(self):
        self.links_seen = set()

    def process_item(self, item, spider):
        if item['url'] in self.links_seen:
            raise scrapy.exceptions.DropItem("Duplicate item found: %s" % item)
        else:
            self.links_seen.add(item['url'])
            return item
			
class MongDBPipeline(object):
	def __init__(self):
		print "starting MongDBPipeline"
		client = pymongo.MongoClient()
		#db = client.test_database
		#collection = db.test_collection
		#connection = pymongo.Connection(
		#settings['MONGODB_SERVER'],
		#settings['MONGODB_PORT']
		#)
		db = client[settings['MONGODB_DB']]
		self.collection = db[settings['MONGODB_COLLECTION']]
		
	def process_item(self, item, spider):
		valid = True
		#item = collection.find_one({"url": "http://www.zillow.com/homedetails/14558-Oregon-Trl-Victorville-CA-92392/17634391_zpid"})
		if self.collection.find_one({"url":item['url']}) is None:
			self.collection.insert(dict(item))
			#log.msg("Question added to MongoDB database!",level=log.DEBUG, spider=spider)
		return item

class CSVPipeline(object):

	def __init__(self):
		self.files = {}

	@classmethod
	def from_crawler(cls, crawler):
		pipeline = cls()
		crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline

	def spider_opened(self, spider):
		file = open('%s_items.csv' % spider.name, 'w+b')
		self.files[spider] = file
		self.exporter = CsvItemExporter(file)
		self.exporter.include_headers_line=False
		self.exporter.fields_to_export = ["url","status","date","mls","address","price","beds","baths","homesize","lotsize","description","images"]
		self.exporter.start_exporting()

	def spider_closed(self, spider):
		self.exporter.finish_exporting()
		file = self.files.pop(spider)
		file.close()

	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item