from pymongo import MongoClient
from sys import argv
import datetime
import time
import urllib2
import re
from lxml import etree
import lxml
import lxml.html


client = MongoClient()
db = client.zillow
collection = db.listings

def getPrice(page):
	tree = etree.HTML(page)
	element = tree.xpath("//div[contains(@class,'main-row  home-summary-row')]")
	try:
		result = re.findall("\$\d+,\d+,?\d+", etree.tostring(element[0]))
		return result[0]
	except:
		return ""

def getStatus(page):
	tree = etree.HTML(page)
	try:
		element = tree.xpath("normalize-space(//span[contains(@id,'listing-icon')]/following-sibling::text())")
		if element == "":
			raise IndexError
		return element
	except IndexError:
		try:
			element = tree.xpath("normalize-space(//span[contains(@id,'listing-icon')]/following-sibling::span)")
			return element
		except:
			return ""


	
urlList=[]
for item in collection.find():
	urlList.append(item['url'])


for url in urlList:
	print url
	page = urllib2.urlopen(url).read()
	time.sleep(2)
	status = getStatus(page)
	print status
	price = getPrice(page)
	print price
	collection.update_one({'url': url}, {'$set': {'status': status}})
	if price != "":
		collection.update_one({'url': url}, {'$set': {'price': price}})
	print ''
