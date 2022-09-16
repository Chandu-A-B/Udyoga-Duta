# updated date,

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
    siteName = "STUDYCAFE.IN"
    baseScrapeUrl = "https://studycafe.in/category/jobs/"
    domainUrl = "https://studycafe.in/"
    # keywords = ["freshers"]

    scrapedData = {}
    links = []
    titles = []
    updatedDates = []
    scrapeDates = []

    tags = "fresher-jobs"
    for pageNumber in range(1, 2):
        queryUrl = baseScrapeUrl + "/page/" + str(pageNumber)
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
        pageSource = requests.get(queryUrl, headers=headers)
        if pageSource.status_code != 200:
            err = "studycafe: err: Response code -  " + str(pageSource.status_code)
            err_logs.append(err)
            continue
        try:
            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
        except:
            err = "studycafe: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
            err_logs.append(err)
            continue

        for item in parsedSource.find_all("div", class_="related-box"):
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

    # DataFrame creation
    studycafeDF = pd.DataFrame(scrapedData)
    if studycafeDF.empty:
        err = "studycafe: err: Empty dataframe"
        err_logs.append(err)
        return None
    studycafeDF = processData(studycafeDF).reindex(columns=["title", "company", "application_link", "article_link", "site", "tags", "updated_date", "scraped_date"])
    return studycafeDF

def processData(rawDF):
    global companies, offLinks, updatedDates
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
        err = "studycafe: article: err: Response code -  " + str(pageSource.status_code)
        err_logs.append(err)
        return
    try:
        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
    except:
        err = "studycafe: article: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
        err_logs.append(err)
        return

    selectedTag = parsedSource.find("div", class_="single-heading1").find("p").text.split("|")[1].strip()
    currentDate = datetime.strptime(selectedTag, "%B %d, %Y").strftime("%d-%m-%Y")

    for eachTag in parsedSource.find("div", class_="single-content").find_all("p"):
        if "is hiring" in eachTag.text:
            company = str(eachTag.text).split("is hiring")[0].strip()
        if re.search("^To Apply ", eachTag.text):
            link = eachTag.find("a")["href"]

    return company, link, currentDate

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    # scraper()
    print(scraper())