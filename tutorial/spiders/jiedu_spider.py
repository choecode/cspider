import scrapy
from tutorial.items import JiedulItem
import json
import re

class ListSpider(scrapy.Spider):
    name = "jiedu"
    allowed_domains = ["www.paoluma.com"]
    headers = {
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0"
    }

    start = 1

    def start_requests(self):
        url = 'https://www.paoluma.com/wp-admin/admin-ajax.php?action=zrz_load_more_posts'
        data = {
            'type': 'collection40',
            'paged':str(self.start)

        }
        yield scrapy.FormRequest(url, method='POST', headers=self.headers, formdata=data, callback=self.parse_list, dont_filter = True)

    def parse_list(self, response):
        res_data = json.loads(response.body.decode('utf-8'))
        res_code = res_data['status']
        data = json.loads(response.text)
        mresponse = scrapy.Selector(text=data['msg'], type="html")
        #list = mresponse.xpath("//div[@class='pos-r pd10 post-list box mar10-b content']")

        if res_code == 200:
            for index, dataitem in enumerate(mresponse.xpath("//div[@class='pos-r pd10 post-list box mar10-b content']")):
                item = JiedulItem()
                item['url'] = dataitem.xpath("//h2/a/@href").extract()[index]
                item['title'] = dataitem.xpath("//h2/a/text()").extract()[index].strip()
                item['time'] = dataitem.xpath("//time/@data-timeago").extract()[index]
                image = dataitem.xpath('//div[@class="preview thumb-in"]').extract()[index]

                matchObj = re.search(r'background-image:url\(\'(.*?)\'\)', image, re.M | re.I)
                if matchObj :
                    item['image'] = matchObj.group(1)
                else :
                    item['image'] = ""

                request = scrapy.Request(item['url'], callback=self.parse_dir_contents)

                request.meta['item'] = item
                yield request

        else:
            print("mei")
        url = 'https://www.paoluma.com/wp-admin/admin-ajax.php?action=zrz_load_more_posts'
        self.start = self.start+1
        data = {
            'type': 'collection40',
            'paged': str(self.start)
        }
        yield scrapy.FormRequest(url, method='POST', headers=self.headers, formdata=data, callback=self.isEmpty,
                                 dont_filter=True)

    def isEmpty(self, response):
        res_data = json.loads(response.body.decode('utf-8'))
        if res_data['msg'] != "":
            return self.parse_list(response)
        else:
            print("无数据列表页")


    def parse_dir_contents(self, response):
        item = response.meta['item']
        # if response.xpath('//div[@id="entry-content"]') == []:
        #     item['content'] = response.xpath('//div[@class="bpp-post-content"]').extract()[0]
        # else:
        #     item['content'] = response.xpath('//div[@class="wxsyncmain"]').extract()[0]
        item['content'] = response.xpath('//div[@id="entry-content"]').extract()[0]
        yield item

