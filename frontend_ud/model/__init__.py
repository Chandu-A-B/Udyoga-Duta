from frontend_ud.app import app
from flask import request, session
from frontend_ud.helpers.database import *
from frontend_ud.helpers.hashpass import *
from frontend_ud.helpers.mailer import *
from bson import json_util, ObjectId
import json
import glob
import os
import pymongo
import sys

from frontend_ud.helpers.hashpass import getHashed

sys.path.append("C:\\Users\\CHANDU\\Documents\\GitHub\\UdyogaDuta\\frontend_ud\\model\\")


def checkloginusername():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    if check is None:
        return "No User"
    else:
        return "User exists"


def checkloginpassword():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    password = request.form["password"]
    hashpassword = getHashed(password)
    if hashpassword == check["password"]:
        sendmail(subject="Login on Flask Admin Boilerplate", sender="Flask Admin Boilerplate", recipient=check["email"],
                 body="You successfully logged in on Flask Admin Boilerplate")
        session["username"] = username
        return "correct"
    else:
        return "wrong"


def checkusername():
    username = request.form["username"]
    check = db.users.find_one({"username": username})
    if check is None:
        return "Available"
    else:
        return "Username taken"


def registerUser():
    fields = [k for k in request.form]
    values = [request.form[k] for k in request.form]
    data = dict(zip(fields, values))
    user_data = json.loads(json_util.dumps(data))
    user_data["password"] = getHashed(user_data["password"])
    user_data["confirmpassword"] = getHashed(user_data["confirmpassword"])
    db.users.insert(user_data)
    sendmail(subject="Registration for Flask Admin Boilerplate", sender="Flask Admin Boilerplate",
             recipient=user_data["email"], body="You successfully registered on Flask Admin Boilerplate")
    print("Done")


def scrapeData_model():
    sys.path.append('model/scrapers/')
    listOfModules = glob.glob("model/scrapers/*.py")
    # print(listOfModules)
    for eachModule in listOfModules:
        nameOfModule = os.path.basename(eachModule).split(".py")[0]
        module = __import__(nameOfModule)
        # print(nameOfModule)
        scraper = getattr(module, 'scraper')

        try:
            resultDF = scraper()
        except Exception as expMesg:
            print(nameOfModule, ": ", expMesg)
            continue
        print(nameOfModule, ": ", "Done !")

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
            # pprint(tempDict)

            try:
                db.scraped_data.insert_one(tempDict)
            except Exception as insertException:
                print(insertException)
            finally:
                # print("\n***\n")
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