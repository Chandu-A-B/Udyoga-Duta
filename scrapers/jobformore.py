from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, date
import re

companies = []
offLinks = []
err_logs = []
updated_dates=[]


def scraper():
    global err_logs
    siteName = "JOBFORMORE.COM"
    baseScrapeUrl = "https://www.jobformore.com/"
    domainUrl = "https://www.jobformore.com/"
    keywords = ["fresher-jobs"]

    scrapedData = {}
    links = []
    titles = []
    updated_dates = []
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
                err = "jobformore: err: Response code -  " + str(pageSource.status_code)
                err_logs.append(err)
                continue
            try:
                parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
            except:
                err = "jobformore: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
                err_logs.append(err)
                continue
            # with open("response.html", "wb") as f:
            #     f.write(pageSource.content)
            # break
            for item in parsedSource.find_all("article"):
                requiredTag = item.find("h2", class_="entry-title").find("a")
                currentArticleTitle = requiredTag.text
                currentArticleLink = requiredTag["href"]
                if currentArticleLink[0] == "/":
                    links.append(domainUrl + currentArticleLink)
                else:
                    links.append(currentArticleLink)
                titles.append(currentArticleTitle)
                # updatedDT = item.find("time")["datetime"]
                # updatedDT = datetime.strptime(updatedDT.split("T")[0], "%Y-%m-%d").strftime("%d-%m-%Y")
                # updatedDates.append(updatedDT)
                scrapeDates.append(datetime.today().strftime("%d-%m-%Y"))

            scrapedData["title"] = titles
            scrapedData["article_link"] = links
            scrapedData["site"] = [siteName] * int(len(titles))
            scrapedData["tags"] = [tags] * int(len(titles))
            # scrapedData["updated_date"] = updatedDates
            scrapedData["scraped_date"] = scrapeDates

    # print(titles)
    # print(links)
    # print(updatedDates)

    # DataFrame creation
    jobformoreDF = pd.DataFrame(scrapedData)
    if jobformoreDF.empty:
        err = "jobformore: err: Empty dataframe"
        err_logs.append(err)
        return None
    jobformoreDF = processData(jobformoreDF).reindex(
        columns=["title", "company", "application_link", "article_link", "site", "tags",
                 "updated_date", "scraped_date"])
    return jobformoreDF


def processData(rawDF):
    global companies, offLinks, updated_dates
    for index, row in rawDF.iterrows():
        company, link, udate = articleScrapper(row["article_link"])
        companies.append(company)
        offLinks.append(link)
        updated_dates.append(udate)
    rawDF.insert(1, "company", companies)
    rawDF.insert(2, "application_link", offLinks)
    rawDF.insert(3, "updated_date", updated_dates)
    return rawDF


def articleScrapper(articleLink):
    global err_logs
    company = link = "N/A"
    updatedDates = []
    queryUrl = articleLink
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110 Safari/537.36"}
    pageSource = requests.get(queryUrl, headers=headers)
    if pageSource.status_code != 200:
        err = "jobformore: article: err: Response code -  " + str(pageSource.status_code)
        err_logs.append(err)
        return
    try:
        parsedSource = BeautifulSoup(pageSource.content, "html.parser", from_encoding="iso-8859-1")
    except:
        err = "jobformore: article: err: Failed to access search url: " + queryUrl + " and convert it to soup object"
        err_logs.append(err)
        return
    companyTag = parsedSource.find_all("p")
    for tag in companyTag:
        resultObj = re.search("^Company: .*", str(tag.text))
        if resultObj is not None:
            company = resultObj.group().split(":")[1].lstrip()

    selectedTag = parsedSource.find("time", class_="entry-date published updated").text
    currentDate = datetime.strptime(selectedTag, "%B %d, %Y").strftime("%d-%m-%Y")
    updatedDates.append(currentDate)

    # updatedDates.append(datetime.strptime(parsedSource.find("time", class_="entry-date published updated").text, "%b %d, %Y").\
    #                     strftime("%d-%m-%Y"))

    link = parsedSource.find("h6").find("a")["href"]
    # with open("response.html", "wb") as f:
    #     f.write(pageSource.content)
    return company, link, updatedDates


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    # scraper()
    print(scraper())
