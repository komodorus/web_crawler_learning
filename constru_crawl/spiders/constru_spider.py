import scrapy

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

        startup_names = response.xpath('/html/body/div[1]/div/div[2]/div[1]/div[1]/table/tbody/tr/td[2]/a/text()').getall()
        startup_ocupation = response.xpath('/html/body/div[1]/div/div[2]/div[1]/div[1]/table/tbody/tr/td[3][not(h3)]/text()').getall()
        startup_links = response.xpath('/html/body/div[1]/div/div[2]/div[1]/div[1]/table/tbody/tr/td[2]/a/@href').getall()

        for num, name in enumerate(startup_names, start=0):
            self.startup_list.append({"name": name})
            self.startup_list[num]["ocupation"] = startup_ocupation[num]

        for url in startup_links:
            yield scrapy.Request(url, callback=self.parse_startup_links)

        print(self.startup_list)

    def parse_startup_links(self, response):
        yield self.get_metrics(response.xpath('//*[@id="company_header"]/div[1]/h1/small/a/@href').get())

    def get_metrics(self, url):
        print(url)
    # @todo Build function to generate XML based on the dict created beforehand 
    # def build_xml(list):
