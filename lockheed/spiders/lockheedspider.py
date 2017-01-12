import time
from time import sleep
from scrapy.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http.request import Request
from lockheed.items import LochkeedItem
from scrapy.http import HtmlResponse
import json
import re
from scrapy.exceptions import CloseSpider

L = open('parseInfo', 'w')


def stripUnicode(unimess):
  if re.search('list',str(type(unimess))):
    if len(unimess) >= 1:
      return unimess[0].encode('utf-8').strip()
    else:
      return unimess
  elif (re.search('str|uni', unimess)):
    return unimess.encode('utf-8').strip()
  else:
    return unimess
    
class LochkeedSpider(CrawlSpider):
    name = "lockheedJobStart"
    page = 1
    ajaxURL = "http://search.lockheedmartinjobs.com/ListJobs/All/Page-"

    def start_requests(self):
      yield Request(self.ajaxURL + str(self.page), callback=self.parse_listings , headers={'Referer':(self.ajaxURL + str(self.page))})

    def parse_listings(self, response):
        c = 0
        jobs = response.xpath('//@href').extract()

        #print jobs


        jSet = set()
        for j in jobs:
          jSet.add(j)


        L.write(str(len(jobs))+'  -  '+str(self.page)+'\n')
        for job_url in jSet:
          if re.search('ShowJob', job_url):
            c += 1
            L.write("\tGenerated URL for job #: "+str(c)+'\n')
            job_url = 'http://search.lockheedmartinjobs.com' + job_url
            job_url = self.__normalise(job_url)
            yield Request(url=job_url, callback=self.parse_details)

        # go to next page...
        self.page += 1
        #sleep(30)
        if self.page == 187:
          L.write("Just  hit the magic number.. finishing up now!")
          #raise CloseSpider("No more pages... exiting...")
        else:
          yield Request(self.ajaxURL + str(self.page), callback=self.parse_listings, headers={'Referer':(self.ajaxURL + str(self.page))})


    
    def parse_details(self, response):
      sel = Selector(response)
      job = sel.xpath('//*[@id="job-table"]')
      item = LochkeedItem()
      # Populate job fields
      item['title'] = job.xpath('//*[@id="content"]/div/div/header/h1/text()').extract()
      item['description'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[3]/div[2]').extract()
      item['f01'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[4]').extract()
      item['f02'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[5]').extract()
      item['f03'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[6]').extract()
      item['f04'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[7]').extract()
      item['f05'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[8]').extract()
      item['f06'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[9]').extract()
      item['f07'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[10]').extract()
      item['f08'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[11]').extract()
      item['f09'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[12]').extract()
      item['f10'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[13]').extract()
      item['f11'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[14]').extract()
      item['f12'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[15]').extract()
      item['f13'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[2]/div[16]').extract()
      item['applink'] = job.xpath('//*[@id="content"]/div/div/div[2]/div/div[1]/a/@href').extract()
      item['page_url'] = response.url
      item = self.__normalise_item(item, response.url)
      item['title'] = stripUnicode(item['title'])
      item['description'] = stripUnicode(item['description'])
      item['applink'] = stripUnicode(item['applink'])
      item['f01'] = stripUnicode(item['f01'])
      item['f02'] = stripUnicode(item['f02'])
      item['f03'] = stripUnicode(item['f03'])
      item['f04'] = stripUnicode(item['f04'])
      item['f05'] = stripUnicode(item['f05'])
      item['f06'] = stripUnicode(item['f06'])
      item['f07'] = stripUnicode(item['f07'])
      item['f08'] = stripUnicode(item['f08'])
      item['f09'] = stripUnicode(item['f09'])
      item['f10'] = stripUnicode(item['f10'])
      item['f11'] = stripUnicode(item['f11'])
      item['f12'] = stripUnicode(item['f12'])
      item['f13'] = stripUnicode(item['f13'])

      L.write((str(item['page_url']))+"\n")
      return item



    def __normalise_item(self, item, base_url):
      '''
      Standardise and format item fields
      '''
      # Loop item fields to sanitise data and standardise data types
      for key, value in vars(item).values()[0].iteritems():
        item[key] = self.__normalise(item[key])
        # Convert job URL from relative to absolute URL
        #item['job_url'] = self.__to_absolute_url(base_url, item['job_url'])
        return item

    def __normalise(self, value):
      # Convert list to string
      value = value if type(value) is not list else ' '.join(value)
      # Trim leading and trailing special characters (Whitespaces, newlines, spaces, tabs, carriage returns)
      value = value.strip()
      return value

    def __to_absolute_url(self, base_url, link):
      '''
      Convert relative URL to absolute URL
      '''
      import urlparse
      link = urlparse.urljoin(base_url, link)
      return link

    def __to_int(self, value):
      '''
      Convert value to integer type
      '''
      try:
        value = int(value)
      except ValueError:
        value = 0
      return value

    def __to_float(self, value):
      '''
      Convert value to float type
      '''
      try:
        value = float(value)
      except ValueError:
        value = 0.0
      return value
