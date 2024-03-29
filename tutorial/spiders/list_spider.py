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

    ##
    #
    # INSERT INTO wordpress.wp_posts ( post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status, comment_status, ping_status, post_password, post_name, to_ping, pinged, post_modified, post_modified_gmt, post_content_filtered, post_parent, guid, menu_order, post_type, post_mime_type, comment_count) VALUES ( 1, '2019-09-18 16:06:53', '2019-09-18 08:06:53', '<p>test content</p>', 'test title', '', 'publish', 'open', 'open', '', 'test-title', '', '', '2019-09-18 16:06:53', '2019-09-18 08:06:53', '', 0, '', 0, 'post', '', 0);
    #
    #
    # ##
    start_urls = [
        "https://www.ra3.cn/activity/woolen/list_1.html",
    ]

    def parse(self, response):
        for data in response.xpath("//ul[@class='left-item']/li"):
            item = TutorialItem()
            item['url'] = "https://www.ra3.cn/" + data.xpath("h3/a/@href").extract()[0]
            if data.xpath("h3/a/b/text()") == []:
                item['title'] = data.xpath("h3/a/text()").extract()[0].strip()
            else:
                item['title'] = data.xpath("h3/a/b/text()").extract()[0].strip()
            item['date'] = data.xpath("span[@class='time']/text()").extract()[0]
            url = "https://www.ra3.cn/" + data.xpath("h3/a/@href").extract()[0]
            request = scrapy.Request(url, callback=self.parse_dir_contents)
            request.meta['item'] = item
            yield request
        next_url = response.url.split('/')
        print("下一页链接地址》》》", next_url)
        number = int(''.join(list(filter(str.isdigit, next_url[-1]))))
        next_url[-1] = 'list_' + str(number + 1) + '.html'
        next_url = '/'.join(next_url)
        print("下一页链接地址》》》", next_url)
        yield scrapy.Request(next_url, callback=self.isEmpty)

    def isEmpty(self, response):
        if response.xpath('//body') != []:
            return self.parse(response)
        else:
            print("这是一个",response.xpath("//title/text()").extract()[0])
    def parse_dir_contents(self, response):
        item = response.meta['item']
        item['content'] = response.xpath('//div[@id="zoomtext"]').extract()[0]
        yield item
