#  all 8 columns available

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
    siteName = "CYBERTECZ.IN"
    baseScrapeUrl = "https://jobs.cybertecz.in/category/"
    domainUrl = "https://jobs.cybertecz.in/"
    keywords = ["freshers"]

    scrapedData = {}
    links = []
    titles = []
    updatedDates = []
    scrapeDates = []
    # Comma separated tags, common across scrappers
    tags = "fresher-jobs"
    for keyword in keywords:
        # change the range function's upperlimit to change number of pages to scrape
        for pageNumber in range(1, 2):
            queryUrl = baseScrapeUrl + keyword + "/page/" + str(pageNumber)
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
            pageSource = requests.get(queryUrl, headers=headers)
            if pageSource.status_code != 200:
                err = "cybertecz: err: Response code -  " + str(pageSource.status_code)
                err_logs.append(err)
                continue
            try:
                parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
            except:
                err = "cybertecz: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                err_logs.append(err)
                continue
            for item in parsedSource.find_all("div", class_="td-module-thumb"):
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
    cyberteczDF = pd.DataFrame(scrapedData)
    if cyberteczDF.empty:
        err = "cybertecz: err: Empty dataframe"
        err_logs.append(err)
        return None
    cyberteczDF = processData(cyberteczDF).reindex(
        columns=["title", "company", "application_link", "article_link", "site", "tags",
                 "updated_date", "scraped_date"])
    return cyberteczDF


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
        err = "cybertecz: article: err: Response code -  " + str(pageSource.status_code)
        err_logs.append(err)
        return
    try:
        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
    except:
        err = "cybertecz: article: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
        err_logs.append(err)
        return

    updatedDT = parsedSource.find("time", class_="entry-date updated td-module-date")["datetime"]
    updated_date = datetime.strptime(updatedDT.split("T")[0], "%Y-%m-%d").strftime("%d-%m-%Y")

    companyTag = parsedSource.find("div", class_="td-post-content").find_all("p")
    for tag in companyTag:
        resultObj = re.search("^Company Name:.*", str(tag.text)) or re.search("^Company:.*", str(tag.text))
        if resultObj is not None:
            company = resultObj.group().split(":")[1].lstrip().rstrip()

        linkTagObj = re.search("^Apply Link: .*", str(tag.text)) or re.search("^To Apply:.*", str(tag.text))
        if linkTagObj is not None:
            link = tag.find("a")["href"]

    # with open("response.html", "wb") as f:
    #     f.write(pageSource.content)
    return company, link, updated_date


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    # scraper()
    print(scraper())