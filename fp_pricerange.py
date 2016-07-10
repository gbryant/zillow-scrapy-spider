from pymongo import MongoClient
import datetime
from sys import argv

client = MongoClient()
db = client.zillow
collection = db.listings

def average_price():
	count=0
	totalPrice=0
	for item in collection.find():
		price = item['price'].replace("$","").replace(",","")
		if price == "":
			price=0
		else:
			price=int(price)
		totalPrice = totalPrice + price
		count = count + 1
	return (totalPrice/count,count)

#	print 'average price of ',average_price()[1],' properties is ',average_price()[0]

while True:
	pass

propertyList=[]
for item in collection.find():
	try:
		price = int(item['price'].replace("$","").replace(",",""))
		if price > int(argv[1]) and price < int(argv[2]):
			if item['beds'] >= argv[3]:
				propertyList.append(item['url'])
	except ValueError:
		pass
		#print "error: ",item['price']


for i in propertyList:		
	print i