import scrapy
import re
from bs4 import BeautifulSoup
from datetime import date, timedelta
from zillow.items import ZillowItem
import pymongo
from scrapy.conf import settings


class ZillowSpider(scrapy.Spider):
	name = "zillow"
	allowed_domains = ["www.zillow.com"]
	start_urls = [
		"http://www.zillow.com/search/GetResults.htm?spt=homes&status=100000&lt=111101&ht=111111&pr=,&mp=,&bd=0%2C&ba=0%2C&sf=,&lot=,&yr=,&pho=0&pets=0&parking=0&laundry=0&pnd=0&red=0&zso=0&days=any&ds=all&pmf=0&pf=0&zoom=10&rect=-117633705,34207259,-117022591,34518438&p=1&sort=days&search=list&disp=1&rid=45732&rt=6&listright=true&isMapSearch=false&zoom=10",
		"http://www.zillow.com/search/GetResults.htm?spt=homes&status=100000&lt=111101&ht=111111&pr=,&mp=,&bd=0%2C&ba=0%2C&sf=,&lot=,&yr=,&pho=0&pets=0&parking=0&laundry=0&pnd=0&red=0&zso=0&days=any&ds=all&pmf=0&pf=0&zoom=10&rect=-117678337,34375179,-117067223,34685734&p=1&sort=days&search=list&disp=1&rid=27683&rt=6&listright=true&isMapSearch=false&zoom=10",
		"http://www.zillow.com/search/GetResults.htm?spt=homes&status=100000&lt=111101&ht=111111&pr=,&mp=,&bd=0%2C&ba=0%2C&sf=,&lot=,&yr=,&pho=0&pets=0&parking=0&laundry=0&pnd=0&red=0&zso=0&days=any&ds=all&pmf=0&pf=0&zoom=9&rect=-117768631,34241324,-116546402,34862271&p=1&sort=days&search=list&disp=1&rid=50742&rt=6&listright=true&isMapSearch=false&zoom=9"
	]
	
	def __init__(self, *args, **kwargs):
		super(ZillowSpider, self).__init__(*args, **kwargs)
		self.existingproperties = []
		client = pymongo.MongoClient()
		db = client[settings['MONGODB_DB']]
		collection = db[settings['MONGODB_COLLECTION']]
		for item in collection.find():
			self.existingproperties.append(item['url'])
		print "existing property count: ",len(self.existingproperties)

	def parseDetails(self, response):
		print "parsing details"
		item = response.meta['item']
		#url already set
		try:
			status = response.selector.xpath("normalize-space(//span[contains(@id,'listing-icon')]/following-sibling::text())")[0].extract()
			if status == "":
				raise IndexError
			item['status'] = status
		except IndexError:
			try:
				item['status'] = response.selector.xpath("normalize-space(//span[contains(@id,'listing-icon')]/following-sibling::span)").extract()[0]
			except IndexError:
				item['status'] = ""
		try:
			daysOld = response.selector.xpath("//li").re("(\d+) day.* on Zillow")[0]
			d = date.today() - timedelta(int(daysOld))
			item['date'] = d.isoformat()
		except IndexError:
			item['date'] = ""
		try:
			item['mls'] = response.selector.xpath("//li").re("MLS #: (.*?\d+)")[0]
		except IndexError:
			item['mls'] = ""
		try:
			#soup = BeautifulSoup(response.selector.xpath("//header[contains(@class,'zsg-content-header addr')]//h1")[0].extract())
			#item['address'] = soup.get_text()
			item['address'] = response.selector.xpath("//meta[contains(@property,'address')]/@content").extract()[0]
		except IndexError:
			item['address'] = ""
		try:
			item['price'] = response.selector.xpath("//div[contains(@class,'main-row  home-summary-row')]").re("\$\d+,\d+,?\d+")[0]
		except IndexError:
			item['price'] = ""
		try:
			item['beds'] = response.selector.xpath('//span').re("(\d+) bed")[0]
		except IndexError:
			item['beds'] = ""
		try:
			item['baths'] = response.selector.xpath('//span').re("(\d+) bath")[0]
		except IndexError:
			item['baths'] = ""
		try:
			item['homesize'] = response.selector.xpath('//span').re("(\d?[,]?\d+) sqft")[0]
		except IndexError:
			item['homesize'] = ""
		try:
			item['lotsize'] = response.selector.xpath('//li').re('Lot: (.*\d [a-z]+)')[0]
		except IndexError:
			item['lotsize'] = ""
		try:
			soup = BeautifulSoup(response.selector.xpath("//div[contains(@class,'hdp-header-description')]//div[contains(@class,'notranslate')]['text()']")[0].extract())
			item['description'] = soup.get_text()
		except IndexError:
			item['description'] = ""
		item['image_urls'] = response.selector.xpath("//a[contains(@class,'show-lightbox')]//img['text()']").re("http.*?\.jpg")
		#images gets set in pipeline
		yield item
	
	def parse(self, response):
		print("PARSING-----------------------------------------------------------")

		pages = response.selector.re("numPages\":(\d+)")
		lastPage=int(pages[0])
		print "last page: "+str(lastPage)
		result = re.match(".*&p=(\d+)&.*", response.url)
		currPage=int(result.group(1))
		print "current page: "+str(currPage)
		
		urlList = re.findall("homedetails.*?zpid",response.body)
		urlList = list(set(urlList))
		
		for i in urlList:
			if "http://www.zillow.com/"+i not in self.existingproperties:
				item = ZillowItem(url="http://www.zillow.com/"+i)
				request = scrapy.Request("http://www.zillow.com/"+i,callback=self.parseDetails)
				request.meta['item'] = item
				print "yielding request: "+"http://www.zillow.com/"+i
				yield request
		nextPage = str(currPage+1)
		theUrl = re.sub("(.*&p=)\d+(&.*)","\g<1>"+nextPage+"\g<2>",response.url)
		if currPage < lastPage:
			#pass
			#comment/uncomment below to crawl all results or not
			yield scrapy.Request(theUrl,callback=self.parse)