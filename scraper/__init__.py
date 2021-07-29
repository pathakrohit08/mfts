import requests
from bs4 import BeautifulSoup as bs

def get_live_data(STOCK_TICKR,verbose=False):
    if verbose:
        print(f'##########################{STOCK_TICKR}##########################')
    STOCK_BASE_URL=f'https://finance.yahoo.com/quote/{STOCK_TICKR}?p={STOCK_TICKR}'
    data=requests.get(STOCK_BASE_URL)
    soup = bs(data.content, 'html.parser')
    dataDict={}
    for div in soup.findAll('div',attrs={'data-test':'quote-header'}):
        t=div.find_all('span')
        dataDict['Close Price']=t[3].text

    for summary_table in ['left-summary-table','right-summary-table']:
        for div in soup.findAll('div',attrs={'data-test':summary_table}):
            table_data=next(div.descendants)
            for row in table_data.find_all('tr'):
                columns = row.find_all('td')
                if len(columns)==2:
                    c=columns[1].find_all('span')
                    spans=columns[1].find_all('span')
                    if len(spans)>0:
                        dataDict[columns[0].find_all('span')[0].text]=columns[1].find_all('span')[0].text
                    else:
                        dataDict[columns[0].find_all('span')[0].text]=columns[1].text

    return dataDict

def get_historic_data(csv_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    req = requests.get(csv_url,headers=headers)
    url_content = req.content
    return url_content

def scrape_news(STOCK_TICKR):
    """helper function to scrape yahoo news for a tickr page"""
    STOCK_BASE_URL=f'https://finance.yahoo.com/quote/{STOCK_TICKR}/news?p={STOCK_TICKR}'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

    data=requests.get(STOCK_BASE_URL,headers=headers)
    soup = bs(data.content, 'html.parser')
    cards=soup.find_all('div','NewsArticle')
    print(len(cards))
    for div in soup.findAll('div',{'id':'latestQuoteNewsStream-0-Stream'}):
        #print(div)
        lis = div.find_all('li',{'class':'js-stream-content'})
        for l in lis:
            print(l.text)
            print('\n')

    print("completed")


if __name__=='__main__':
    scrape_news("AAPL")