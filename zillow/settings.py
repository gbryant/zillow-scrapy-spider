# -*- coding: utf-8 -*-

# Scrapy settings for zillow project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'zillow'

SPIDER_MODULES = ['zillow.spiders']
NEWSPIDER_MODULE = 'zillow.spiders'

DOWNLOAD_DELAY=5
LOG_ENABLED=False

USER_AGENT="Mozilla/5.0 (Windows NT 6.3; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0"

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "zillow"
MONGODB_COLLECTION = "listings"

IMAGES_STORE = '/home/Gregory/Spiders/ZillowSpider/images'

ITEM_PIPELINES = {
    'zillow.pipelines.DuplicatesPipeline': 400,
	'scrapy.contrib.pipeline.images.ImagesPipeline': 500,
	'zillow.pipelines.MongDBPipeline':600
	}
#'zillow.pipelines.CSVPipeline':600


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'zillow (+http://www.yourdomain.com)'
