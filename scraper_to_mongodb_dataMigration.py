import pymongo
import json
import os
import glob
from pprint import pprint
import sys

with open("db_config.json", "r") as f:
    credentials = json.load(f)

try:
    client = pymongo.MongoClient(host=credentials["host"], port=credentials["port"])
except Exception as e:
    print(e)
    exit(-1)
finally:
    print("Database Connection is successful")
    # noinspection PyUnboundLocalVariable
    db = client.UdyogaDuta
    collection = db.scraped_data

sys.path.append('scrapers/')
listOfModules = glob.glob("scrapers/*.py")
# print(listOfModules)
for eachModule in listOfModules:
    nameOfModule = os.path.basename(eachModule).split(".py")[0]
    module = __import__(nameOfModule)
    # print(nameOfModule)
    scraper = getattr(module, 'scraper')
    resultDF = scraper()
    for index, eachRow in resultDF.iterrows():
        tempDict = {
            "title": eachRow["title"],
            "company": eachRow["company"],
            "application_link": eachRow["application_link"],
            "article_link": eachRow["article_link"],
            "site": eachRow["site"],
            "tags": eachRow["tags"],
            "updated_date": eachRow["updated_date"],
            "scraped_date": eachRow["scraped_date"],
            "module": nameOfModule
        }
        pprint(tempDict)
        try:
            collection.insert_one(tempDict)
        except Exception as insertException:
            print(insertException)
        finally:
            print("\n***\n")
            tempDict = {
                "title": None,
                "company": None,
                "application_link": None,
                "article_link": None,
                "site": None,
                "tags": None,
                "updated_date": None,
                "scraped_date": None,
                "module": None
            }