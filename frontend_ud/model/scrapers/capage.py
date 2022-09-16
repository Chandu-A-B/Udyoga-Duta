# all 8 tags available

from bs4 import  BeautifulSoup
import requests
import pandas as pd
from datetime import datetime , date
import re

companies = []
offLinks = []
updatedDates= []
err_logs = []

def scraper():
    global err_logs
    siteName = "CAPAGE.IN"
    baseScrapeUrl = "https://capage.in/jobs/"
    domainUrl = "https://capage.in/"
    # keywords = ["freshers"]

    scrapedData = { }
    links = []
    titles = []
    updatedDates = []
    scrapedDates = []

    # Comma separated tags, common across scrappers

    # change the range function's upperlimit to change number of pages to scrape
    tags = "freshers-jobs"
    for pageNumber in range(1, 2):
        queryUrl = baseScrapeUrl + "page/" + str(pageNumber)
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3209.110 Safari/537.36"}
        pageSource = requests.get(queryUrl, headers=headers)
        if pageSource.status_code != 200:
            err = "capage: err: Response code - " + str(pageSource.status_code)
            err_logs.append(err)
            continue
        try:
            parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
        except:
            err = " capage: err: Failed to access search url: " + queryUrl + "and convert it to soup object"
            err_logs.append(err)
            continue
        # print(parsedSource.find_all("article"))
        for item in parsedSource.find_all("article", class_="latestPost excerpt"):
            requiredTag = item.find("a")
            currentArticleTitle = requiredTag["title"]
            currentArticleLink = requiredTag["href"]
            if currentArticleLink[0] == "/":
                links.append(domainUrl + currentArticleLink)
            else:
                links.append(currentArticleLink)
            titles.append(currentArticleTitle)
            scrapedDates.append(datetime.today().strftime("%d-%m-%Y"))


        scrapedData["title"] = titles
        scrapedData["article_link"] = links
        scrapedData["scraped_date"] = scrapedDates
        scrapedData["site"] = [siteName] * int(len(titles))
        scrapedData["tags"] = [tags] * int(len(titles))

    # DataFrame creation
    capageDF = pd.DataFrame(scrapedData)
    if capageDF.empty:
        err = "capage: err: Empty dataframe"
        err_logs.append(err)
        return None

    capageDF = processData(capageDF).reindex(columns = ["title", "company", "application_link", "article_link", "site", "tags", "updated_date", "scraped_date"])
    return  capageDF

def processData(rawDF):
    global companies, offLinks
    for index, row in rawDF.iterrows():
        updated_date, company, link = articleScrapper(row["article_link"])

        updatedDates.append(updated_date)
        companies.append(company)
        offLinks.append(link)
    rawDF.insert(1, "updated_date", updatedDates)
    rawDF.insert(2, "company", companies)
    rawDF.insert(2, "application_link", offLinks)

    return rawDF

def articleScrapper(articleLink):
    global err_logs
    company = link = updated_date = "N/A"
    queryUrl = articleLink
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"
    }
    pageSource = requests.get(queryUrl, headers=headers)
    if pageSource.status_code !=200:
        err = "capage: article: err: Response code - " + str(pageSource.status_code)
        err_logs.append(err)
        return
    try:
        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
    except:
        err = "capage: article: arr: Failed to access search url: " + queryUrl + " and convert it to soup object"
        err_logs.append(err)
        return

    updatedDT = parsedSource.find("span", class_="thetime date updated").find("span").text
    updated_date = datetime.strptime(updatedDT, "%B %d, %Y").strftime("%d-%m-%Y")

    for eachTag in parsedSource.find("div", class_="post-single-content box mark-links entry-content").find_all("p"):
        if "Recruiting" in eachTag.text:
            company = str(eachTag.text).split("Recruiting")[0].strip()
        if re.search("^Click here", eachTag.text):
            link = eachTag.find("a")["href"]


    return updated_date, company, link


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    # scraper()
    print(scraper())
