# all 8 links available

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
    siteName = "ENGGWAVE.COM"
    baseScrapeUrl = "https://www.enggwave.com/category/mca-jobs"
    domainUrl = "https://www.enggwave.com/"
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
            err = "enggwave: err: Response code -  " + str(pageSource.status_code)
            err_logs.append(err)
            continue
        try:
            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
        except:
            err = "enggwave: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
            err_logs.append(err)
            continue

        for item in parsedSource.find_all("h3", class_="jeg_post_title"):
            requiredTag = item.find("a")
            currentArticleTitle = item.find("a").text
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
    enggwaveDF = pd.DataFrame(scrapedData)
    if enggwaveDF.empty:
        err = "enggwave: err: Empty dataframe"
        err_logs.append(err)
        return None
    enggwaveDF = processData(enggwaveDF).reindex(columns=["title", "company", "application_link", "article_link", "site", "tags", "updated_date", "scraped_date"])
    return enggwaveDF

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
        err = "enggwave: article: err: Response code -  " + str(pageSource.status_code)
        err_logs.append(err)
        return
    try:
        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
    except:
        err = "enggwave: article: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
        err_logs.append(err)
        return


    for eachTag in parsedSource.find("div", class_="wpb_wrapper").find_all("p"):
        if re.search("^Company:", eachTag.text):
            company = eachTag.text.split("Company:")[1].strip()
            company = str(company.split()[0]) + " " + str(company.split(company.split()[0])[1]).strip()

        if re.search("^Apply Link:", eachTag.text):
            link = eachTag.find("a")["href"]




    selectedTag = parsedSource.find("div", class_="jeg_meta_date").find("a").text
    currentDate = datetime.strptime(selectedTag, "%B %d, %Y").strftime("%d-%m-%Y")

    return company, link, currentDate

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    # scraper()
    print(scraper())