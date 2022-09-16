# all 8 columns available

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
    siteName = "JAGRANJOSH.COM"
    baseScrapeUrl = "https://www.jagranjosh.com/search/post-graduate_sarkari-naukri"
    domainUrl = "https://www.jagranjosh.com/"
    # keywords = ["freshers"]

    scrapedData = {}
    links = []
    titles = []
    updatedDates = []
    scrapeDates = []

    tags = "fresher-jobs"
    for pageNumber in range(1, 2):
        queryUrl = baseScrapeUrl + "_" + str(pageNumber)
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
        pageSource = requests.get(queryUrl, headers=headers)
        if pageSource.status_code != 200:
            err = "jagranjosh: err: Response code -  " + str(pageSource.status_code)
            err_logs.append(err)
            continue
        try:
            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
        except:
            err = "jagranjosh: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
            err_logs.append(err)
            continue

        for item in parsedSource.find_all("div", class_="ibpsbox"):
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
    jagranjoshDF = pd.DataFrame(scrapedData)
    if jagranjoshDF.empty:
        err = "jagranjosh: err: Empty dataframe"
        err_logs.append(err)
        return None
    jagranjoshDF = processData(jagranjoshDF).reindex(columns=["title", "company", "application_link", "article_link", "site", "tags", "updated_date", "scraped_date"])
    return jagranjoshDF

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
        err = "jagranjosh: article: err: Response code -  " + str(pageSource.status_code)
        err_logs.append(err)
        return
    try:
        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
    except:
        err = "jagranjosh: article: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
        err_logs.append(err)
        return

    company = "N\A"
    for eachTag in parsedSource.find("div", itemprop="articleBody").find_all("p"):
        if "Recruitment" in eachTag.text and company == "N\A":
            company = str(eachTag.text).split("Recruitment")[0].strip()

    selectedTag = parsedSource.find("span", class_="date-article").text.split("Modified On:")[1].split('IST')[0].strip()
    currentDate = datetime.strptime(selectedTag, "%B %d, %Y %H:%M").strftime("%d-%m-%Y")

    application_link = "N\A"
    tempTags = parsedSource.find_all("div")
    for eachTag in tempTags:
        if eachTag.get("itemprop") == "articleBody":
            tempTags = parsedSource.find_all("p")

    for newEachTag in tempTags:
        if application_link == "N\A" and newEachTag.find("a"):
            application_link = newEachTag.find("a")["href"]

    # link = parsedSource.find("strong").find("a")["href"]
    # with open("response.html", "wb") as f:
    #     f.write(pageSource.content)
    return company, application_link, currentDate

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    # scraper()
    print(scraper())
