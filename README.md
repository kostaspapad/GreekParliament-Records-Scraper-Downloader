# GreekParliament-Records-Scraper-Downloader

Python crawler-downloader for greek parliaments conference records.

## Scraper
### Dependencies:
        BeautifulSoup, Requests, sqlite3, pandas

## Usage
First create a database table on sqlite, the file 'vouliDBschema' describes the schema that is used.
### Crawl page specified by number example 
        python scraper.py -p <number> or --pagecrawl <number>
### Start crawling from page specified by number
        python scraper.py -f <number> or --startfrom <number>
### Crawl all pages
        python scraper.py -a or --all

The data are extracted and stored to sqlite db. The db file can be used as input to the downloader script.

## Downloader
### Dependensies:
        sqlite3, urllib2, requests

## Usage 
### Download single doc file
        python recordsDownload.py -d or --download  '/UserFiles/32323-2312382-232852-2929/es2828582.doc'
### Download single file specified by ID in database
        python recordsDownload.py -f or --fromID <id>
### Download all doc files
        python recordsDownload.py -a or --all
