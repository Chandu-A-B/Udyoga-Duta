# company

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, date
import re

companies = []
offLinks = []
updatedDates = []
err_logs = []

def scraper():
    global err_logs
    siteName = "QUIZXP.COM"
    baseScrapeUrl = "https://quizxp.com/"
    domainUrl = "https://quizxp.com/"
    # keywords = ["freshers"]

    scrapedData = {}
    links = []
    titles = []
    updatedDates = []
    scrapeDates = []

    # change the range function's upperlimit to change number of pages to scrape
    tags = "freshers"
    for pageNumber in range(1, 2):
        queryUrl = baseScrapeUrl + "/page/" + str(pageNumber)
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
        pageSource = requests.get(queryUrl, headers=headers)
        if pageSource.status_code != 200:
            err = "quizxp: err: Response code -  " + str(pageSource.status_code)
            err_logs.append(err)
            continue
        try:
            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
        except:
            err = "quizxp: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
            err_logs.append(err)
            continue

        for item in parsedSource.find_all("div", class_="nv-post-thumbnail-wrap"):
            requiredTag = item.find("a")
            currentArticleTitle = requiredTag["title"]
            currentArticleLink = requiredTag["href"]
            if currentArticleLink[0] == "/":
                links.append(domainUrl + currentArticleLink)
            else:
                links.append(currentArticleLink)
            titles.append(currentArticleTitle)
            scrapeDates.append(datetime.today().strftime("%d-%m-%Y"))

        scrapedData["title"] = titles
        scrapedData["article_link"] = links
        scrapedData["scraped_date"] = scrapeDates
        scrapedData["site"] = [siteName] * int(len(titles))
        scrapedData["tags"] = [tags] * int(len(titles))

    #DataFrame creation
    quizxpDF = pd.DataFrame(scrapedData)
    if quizxpDF.empty:
        err = "quizxp: err: Empty dataframe"
        err_logs.append(err)
        return None
    quizxpDF = processData(quizxpDF).reindex(columns=["title", "company", "application_link", "article_link", "site", "tags", "updated_date", "scraped_date"])
    return quizxpDF

def processData(rawDF):
    global companies, offLinks
    for index, row in rawDF.iterrows():
        company, link, updated_date = articleScrapper(row["article_link"])
        companies.append(company)
        offLinks.append(link)
        updatedDates.append(updated_date)
    rawDF.insert(1, "company", companies)
    rawDF.insert(2, "application_link", offLinks)
    rawDF.insert(4, "updated_date", updatedDates)
    return rawDF

def articleScrapper(articleLink):
    global err_logs
    company = link = updated_date = "N/A"
    queryUrl = articleLink
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
    pageSource = requests.get(queryUrl, headers=headers)
    if pageSource.status_code != 200:
        err = "quizxp: article: err: Response code -  " + str(pageSource.status_code)
        err_logs.append(err)
        return
    try:
        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
    except:
        err = "quizxp: article: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
        err_logs.append(err)
        return

    updatedDT = parsedSource.find("time", class_="entry-date published")["datetime"]
    updated_date = datetime.strptime(updatedDT.split("T")[0], "%Y-%m-%d").strftime("%d-%m-%Y")

    tdFoundFlag = False
    try:
        for tag in parsedSource.find("table", class_="has-fixed-layout").find_all("td"):
            if "Company" in tag.text:
                tdFoundFlag = True
                continue
            else:
                if tdFoundFlag is True:
                    company = tag.text
                    tdFoundFlag = False
                    break
    except AttributeError:
        company = "N\A"

    for eachTag in parsedSource.find("div", class_="nv-content-wrap entry-content").find_all("p"):
        if re.search("^Apply Link:", eachTag.text):
            link = eachTag.find("a")["href"]
    return company, link, updated_date

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    # scraper()
    print(scraper())