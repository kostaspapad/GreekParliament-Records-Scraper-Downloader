import sys, getopt
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urlparse
import datetime
import sqlite3
import warnings
import re
import time

def crawlPage(pageNumber):
    ''' args: number of page for crawling based on pageNo url parameter
        Crawls page and inserts data to sqlite database'''

    url = 'http://www.hellenicparliament.gr/Praktika/Synedriaseis-Olomeleias?pageNo=%d' % (pageNumber)

    # Scrape the HTML at the url
    r = requests.get(url)

    # Turn the HTML into a Beautiful Soup object
    soup = BeautifulSoup(r.text, 'lxml')

    #Create four variables to score the scraped data in
    date = []
    timePeriod = []
    session = []
    conference = []
    relatedVideos = []
    pdfDocumentsLoc = []
    pdfDocuments = []
    documentsLoc = []
    documents = []

    # Create an object of the first object that is class=dataframe
    table = soup.find(class_='grid')

    # Find all the <tr> tag pairs, skip the first two and last one, then for each.
    for row in table.find_all('tr')[2:-1]:

        # Create a variable of all the <td> tag pairs in each <tr> tag pair,
        col = row.find_all('td')

        # Get 11 chars of date
        date.append(col[0].string.strip())

        if col[1].get_text():
            timePeriod.append(col[1].string.strip())
        else:
            timePeriod.append('Empty')

        if col[2].get_text():
            session.append(col[2].string.strip())
        else:
            session.append('Empty')

        if col[3].get_text():
            conference.append(col[3].string.strip())
        else:
            conference.append('Empty')

        if col[4].find('a') is not None:
            relatedVideos.append(col[4].find('a').get('href'))
        else:
            relatedVideos.append('No video')

        if col[5].find('a') is not None:
            # Split location on '/' char to get location and file
            pdflink = col[5].find('a').get('href').split('/')
            pdfDocumentsLoc.append(pdflink[1] + '/' + pdflink[2])
            pdfDocuments.append(pdflink[3])
        else:
            pdfDocumentsLoc.append('No pdf loc')
            pdfDocuments.append('No pdf')

        if col[6].find('a') is not None:
            doclink = col[6].find('a').get('href').split('/')
            documentsLoc.append(doclink[1] + '/' + doclink[2])
            documents.append(doclink[3])
        else:
            documentsLoc.append('No doc loc')
            documents.append('No doc')

    # Create a variable of the value of the columns
    columns = {'Date': date, 'TimePeriod': timePeriod, 'Session': session, 'Conference': conference, 'RelatedVideosLink': relatedVideos, 'PDFdocumentLocation': pdfDocumentsLoc, 'PDF Document':pdfDocuments, 'DocumentLocation':documentsLoc, 'DocumentName': documents, 'DateOfCrawl': datetime.datetime.now().strftime("%d/%m/%Y")}

    # Create a dataframe from the columns variable
    df = pd.DataFrame(columns)

    # Revert frame because the data are crawled from top to bot
    df = df.iloc[::-1]

    # Return frame in json format
    #return df.to_json(orient='records')

    insertToDB(df)

    print "Frame %d inserted" % (pageNumber)

''' Inserts panda frame to sqlite database '''
def insertToDB(df):

    # Create db connection
    conn = sqlite3.connect('voulidatabase.db')

    # Create cursor
    #cur = conn.cursor()

    # Insert dataframe to sqlite
    df.to_sql('vouliData', conn, if_exists="append", index=False)

def getNumberOfPages():

    # Base url
    url = ' http://www.hellenicparliament.gr/Praktika/Synedriaseis-Olomeleias'

    # Make request to url
    r = requests.get(url)

    # Convert to soupObj
    soup = BeautifulSoup(r.text, 'lxml')

    # Find last page url
    lastPageUrl = soup.find(id = 'ctl00_ContentPlaceHolder1_rr_repSearchResults_ctl11_ctl01_repPager_ctl10_lnkLastPage').get('href')

    # Parse url parameters
    parsed = urlparse.urlparse(lastPageUrl)

    # Get parameter pageNo. (pageNumber is list)
    pageNumber = urlparse.parse_qs(parsed.query)['pageNo']

    # Convert single list item to int and return value
    return int(pageNumber[0])


def main(argv):

   try:
        opts, args = getopt.getopt(argv,"hp:f:a",['pageNum='])
   except getopt.GetoptError:
        usage()
        sys.exit(2)

   for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()

        elif opt in ("-p", "--pagecrawl"):
            print 'Single page crawl'
            crawlPage(int(arg))

        elif opt in ("-f", "--startfrom"):
            print "Start from page:", arg
            for i in range(int(arg), 0, -1):
                crawlPage(i)

        elif opt in ("-a", "--all"):
            pageNum = getNumberOfPages()
            print "Crawler started, number of pages to crawl:", pageNum
            start_time = time.time()
            for i in range(pageNum, 0, -1):
                crawlPage(i)
            print("--- %s seconds ---" % (time.time() - start_time))
        else:
            assert False, "unhandled option"

def usage():
    usage = """-----------------------------------
    Vouli scraper v0.1
    Dependencies:
        BeautifulSoup,
        Requests,
        sqlite3,
        pandas

    -h --help                     Print this
    -p --pagecrawl <number>       Crawl page specified by number
    -f --frompage <number>        Start crawling from page specified by number
    -a --all                      Crawl all pages
    -----------------------------------
    """
    print usage

if __name__ == "__main__":

   #Don't show pandas user warnings
   warnings.filterwarnings('ignore')
   main(sys.argv[1:])

