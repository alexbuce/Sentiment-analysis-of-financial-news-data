import scrapy
from bs4 import BeautifulSoup
import sys
import os
import _pickle as pickle
import pandas as pd
sys.path.append("../tut1/tut1/spiders/")
from scrape_with_bs4 import *
import datetime
class ContentSpider(scrapy.Spider):
    name = "yolo"
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    date_=None
    file=None
    url=None
    total_urls=0
    counter=0
    ##these variables store the content scraped
    b={}
    date={}
    contents={}
    total_links={}
    NEWS={'reuters.com':sc_reuters,'thehindu.com':sc_thehindu,'economictimes.indiatimes':sc_econt,
    'moneycontrol.com':moneyControl,'ndtv.com':ndtv,'hindubusinessline.com':hindu_bl}
    #initialises the data types with the respective keys and empty list/dictionary
    for key in NEWS:
        date[key]=[]
        b[key]={}
        contents[key]=[]
        total_links[key]=[]
    #generates all the links to be scraped 
    def start_requests(self):
        print("\n\nEnter company name to scrape content for")
        cos=[i.split('_')[1] for i in list_files('links/finallinks')]
        print('\n'+str(cos))
        self.dest_file=input()
        for file_name in list_files('links/finallinks'):
            if(self.dest_file.lower() in file_name.lower()):
                print("SCRAPING DATA FOR "+file_name)
                links = [line.rstrip('\n') for line in open('links/finallinks/'+file_name)]
                self.total_urls=len(links)
                self.file=file_name
                for l in links:
                    self.date_,self.url=l.split('::')
                    yield scrapy.Request(self.url,self.parse)
    # gets called at the end when all the data has been scraped .
    # It maintains the same folder format for data storage as before.
    def writeTo(self):
                company=self.dest_file
                for webp in self.date:
                    make_directory(company,webp)
                    with open('content/'+company+'/'+webp+'/raw_'+self.file.split('.data')[0]+'_'+webp+'.pkl', 'wb') as fp:
                        pickle.dump(self.b[webp], fp)
                    temp = {'date':self.date[webp],
                            'data':self.contents[webp],
                            'url':self.total_links[webp]
                            }
                    df = pd.DataFrame(temp)
                    df.set_index('date',inplace=True)
                    df.to_pickle('content/'+company+'/'+webp+'/'+self.file.split('.data')[0]+'_'+webp+'_content.pkl')
                    df.to_csv('content/'+company+'/'+webp+'/'+self.file.split('.data')[0]+'_'+webp+'_content.csv')
                    tracker(self.file)

    def parse(self, response):
        for key in self.NEWS:
            if key in response.url:
                bs=BeautifulSoup(response.text,'html.parser')
                content=self.NEWS[key](bs)
                str1=''
                tokens=[]
                for text in content:
                    tokens.extend(text)
                for tk in tokens:
                    str1+=''.join(tk)
                c = datetime.datetime.strptime(self.date_, '%d-%b-%Y')
                self.date[key].append(c)
                self.contents[key].append(str1)
                self.total_links[key].append(response.url)
                temp_={c:str1}
                self.b[key].update(temp_)
                self.counter+=1
                yield self.logger.info("COUNTER -"+str(self.counter)+" #"*15)
                yield self.logger.info("TOTAL URLS -"+str(self.total_urls)+" #"*12)
                if(self.counter==self.total_urls-1):
                    self.writeTo() 
