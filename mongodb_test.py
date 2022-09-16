import pymongo

client = pymongo.MongoClient('localhost', port=27017)

db = client.UdyogaDuta
test = db.Test

employee = {
    "dob": "18-08-2000",
    "company": "Cognizant",
    "branch": "Bengaluru"
}

test.insert_one(employee)