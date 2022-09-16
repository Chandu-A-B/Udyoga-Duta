from app import app
import urllib
import os

# secret key for user session
app.secret_key = "ITSASECRET"


#database connection parameters
connection_params = {
    'user': 'bot',
    'password': "chandu",
    'host': 'localhost',
    'port': '27017',
    'namespace': 'UdyogaDuta',
    'databasename': "UdyogoDuta"
}
