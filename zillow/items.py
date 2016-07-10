# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZillowItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
	url = scrapy.Field()
	status = scrapy.Field()
	date = scrapy.Field()
	mls = scrapy.Field()
	address = scrapy.Field()
	price = scrapy.Field()
	beds = scrapy.Field()
	baths = scrapy.Field()
	homesize = scrapy.Field()
	lotsize = scrapy.Field()
	description = scrapy.Field()
	image_urls = scrapy.Field()
	images = scrapy.Field()
	
	