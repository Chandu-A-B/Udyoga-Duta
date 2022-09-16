import mysql.connector as mysql
import json

try:
    with open("db_config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print("db_config.json file not found in current directory\n")

try:
    conn = mysql.connect(host=config["host"],
                            port=config["port"],
                            database=config["database"],
                            user=config["username"],
                            password=config["password"])
except Exception as e:
    print("Couldn't connect to the database, please check the configuration in \"db_config.json\"\n")
    print(e)
    exit(-1)

print("test")
