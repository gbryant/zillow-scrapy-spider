from pymongo import MongoClient
import datetime
import sys

client = MongoClient()
db = client.zillow
collection = db.listings

item = collection.find_one({'images.path':{'$regex':'.*'+sys.argv[1]+'.*'}})
print item['url']