import scrapy
import json
import csv
import os
import ssl
import urllib.request

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

class ConstruSpider(scrapy.Spider):
    name = "construtechs"
    startup_list = []

    def start_requests(self):

        urls = [
            'https://constructapp.io/pt/100-startups-de-construcao-civil/'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        startup_data = response.xpath('/html/body/div[1]/div/div[2]/div[1]/div[1]/table/tbody/tr[position()>1]')
        
        for startup in startup_data:
            
            if startup.xpath('td[3]/text()').get() is None:
                ocupation = startup.xpath('td[3]/strong/text()').get()
            else:
                ocupation = startup.xpath('td[3]/text()').get()

            self.startup_list.append({
                "name": startup.css('td a::text').get(),
                "ocupation": ocupation
            })

        for num, startup in enumerate(startup_data, start=0):

            url = startup.xpath('td[2]/a/@href').get()
            
            if url is not None:
                yield scrapy.Request(url, callback=self.parse_startup_links, meta={'index': num})
            else:
                self.startup_list[num]["url"] = "null"

    def parse_startup_links(self, response):
        url = response.xpath('//*[@id="company_header"]/div[1]/h1/small/a/@href').get()
        if url is not None:
            self.startup_list[response.meta.get('index')]["url"] = url
        else:
            self.startup_list[response.meta.get('index')]["url"] = "null"

    def get_sharedcount(self):
        for startup in self.startup_list:
            try:
                if startup["url"] == "null":
                    startup["facebook_count"] = "null"
                    print('invalid url')
                else:
                    request_url = 'https://api.sharedcount.com/v1.0/?apikey=91aeac3cae7c46160618baba16dcb1f5df782761&url=' + startup["url"]
                    startup["facebook_count"] = json.load(urllib.request.urlopen(request_url))["Facebook"]["total_count"]
                    print(startup["facebook_count"])
            except KeyError as e:
                print('I got a KeyError - reason "%s"' % str(e))
                print(startup)

    def __del__(self):
        print('iniciando sharedCount')
        self.get_sharedcount()
        print('gerando CSV')
        with open('construtechs_spider.csv', 'w') as f:  
            w = csv.DictWriter(f, self.startup_list[0].keys())
            w.writeheader()
            for row in self.startup_list:
                w.writerow(row)
        print('DONE')
