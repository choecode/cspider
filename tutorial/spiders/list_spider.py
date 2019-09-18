import scrapy
from tutorial.items import TutorialItem
import re


class ListSpider(scrapy.Spider):
    name = "list"
    allowed_domains = ["www.ra3.cn"]
    headers = {
        "host": "www.ra3.cn",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0"
    }
    start_urls = [
        "https://www.ra3.cn/activity/woolen/list_1.html",
    ]

    def parse(self, response):
        for data in response.xpath("/html/body/div[6]/div/div/div[1]/div[2]/ul/li"):
            item = TutorialItem()
            item['url'] = "https://www.ra3.cn/" + data.xpath("h3/a/@href").extract()[0]
            item['title'] = data.xpath("/h3/a/text()").extract()[0].strip()
            item['date'] = data.xpath("span[@class='time']/text()").extract()[0]
            print(item['title'])
            url = "https://www.ra3.cn/" + data.xpath("h3/a/@href").extract()[0]
            request = scrapy.Request(url, callback=self.parse_dir_contents)
            request.meta['item'] = item
            yield request

        next_url = response.url.split('/')
        number = int(''.join(list(filter(str.isdigit, next_url[-1]))))
        next_url[-1] = 'list_' + str(number + 1) + '.html'
        next_url = '/'.join(next_url)
        print("下一页链接地址》》》", next_url)
        yield scrapy.Request(next_url, callback=self.isEmpty)

    def isEmpty(self, response):
        print("全部状态",response.status)
        if response.status == 200:
            return self.parse(response)

    def parse_dir_contents(self, response):
        item = response.meta['item']
        item['content'] = response.xpath('//div[@id="zoomtext"]').extract()[0]
        yield item
