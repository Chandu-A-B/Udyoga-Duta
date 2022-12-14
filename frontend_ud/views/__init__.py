from datetime import datetime
import pprint

from flask import render_template, request, redirect, url_for, session
from frontend_ud.app import app
from frontend_ud.model import *

from frontend_ud.model import registerUser, checkusername


@app.route('/', methods=["GET"])
def home():
    if "username" in session:
        return render_template('index.html')
    else:
        return render_template('login.html')

# Register new user
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        registerUser()
        return redirect(url_for("login"))

#Check if email already exists in the registratiion page
@app.route('/checkusername', methods=["POST"])
def check():
    return checkusername()

# Everything Login (Routes to renderpage, check if username exist and also verifypassword through Jquery AJAX request)
@app.route('/login', methods=["GET"])
def login():
    if request.method == "GET":
        if "username" not in session:
            return render_template("login.html")
        else:
            return redirect(url_for("home"))


@app.route('/checkloginusername', methods=["POST"])
def checkUserlogin():
    return checkloginusername()

@app.route('/checkloginpassword', methods=["POST"])
def checkUserpassword():
    return checkloginpassword()

#The admin logout
@app.route('/logout', methods=["GET"])  # URL for logout
def logout():  # logout function
    session.pop('username', None)  # remove user session
    return redirect(url_for("home"))  # redirect to home page with message

#Forgot Password
@app.route('/forgot-password', methods=["GET"])
def forgotpassword():
    return render_template('forgot-password.html')

#404 Page
@app.route('/404', methods=["GET"])
def errorpage():
    return render_template("404.html")

#Blank Page
@app.route('/blank', methods=["GET"])
def blank():
    return render_template('blank.html')

#Buttons Page
@app.route('/buttons', methods=["GET"])
def buttons():
    return render_template("buttons.html")

#Cards Page
@app.route('/cards', methods=["GET"])
def cards():
    return render_template('cards.html')

#Charts Page
@app.route('/charts', methods=["GET"])
def charts():
    return render_template("charts.html")

#Tables Page
@app.route('/tables', methods=["GET"])
def tables():
    scraped_data = (db.scraped_data.find({}))
    # print(scraped_data)
    return render_template("tables.html", scollection=scraped_data)

#Scrape data Page
@app.route('/scrape-data', methods=["GET"])
def scrapeData():
    # scraped_data = (db.scraped_data.find({"scraped_date": str(datetime.date.today().strftime("dd-mm-yyyy"))}))
    return render_template("scrape_data.html")

# Scrape data Page
@app.route('/scrape-data', methods=["POST"])
def scrapeDataReturn():
    scrapeData_model()
    scraped_data = (db.scraped_data.find({"scraped_date": str(datetime.now().strftime("%d-%m-%Y"))}))
    # scraped_data = (db.scraped_data.find({"scraped_date": "06-07-2022"}))
    return render_template("scraped_data.html", scollection=scraped_data)

#user public page
@app.route('/offers', methods=['GET'])
def offers():
    scraped_data = (db.scraped_data.find({}))
    # print(scraped_data)
    return render_template("public_table.html", scollection=scraped_data)

#Utilities-animation
@app.route('/utilities-animation', methods=["GET"])
def utilitiesanimation():
    return render_template("utilities-animation.html")

#Utilities-border
@app.route('/utilities-border', methods=["GET"])
def utilitiesborder():
    return render_template("utilities-border.html")

#Utilities-color
@app.route('/utilities-color', methods=["GET"])
def utilitiescolor():
    return render_template("utilities-color.html")

#utilities-other
@app.route('/utilities-other', methods=["GET"])
def utilitiesother():
    return render_template("utilities-other.html")
