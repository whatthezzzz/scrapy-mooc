import json

import scrapy
import re
import demjson
from bs4 import BeautifulSoup


class CourseSpider(scrapy.Spider):
    name = 'course'
    allowed_domains = ['icourse163.org']
    start_urls = ['https://www.icourse163.org/course/NUDT-42002']

    # def start_requests(self):
    #     post_url = 'http://fanyi.baidu.com/sug'
    #
    #     # 发送post请求
    #     yield scrapy.FormRequest(url=post_url, callback=self.parse)

    def parse(self, response):
        item = {'term_id': re.search(r'termId : "(\d+)"', response.text).group(1),
                'title': response.xpath("//meta[@name= 'description']/@content").extract_first().split(',')[0],
                'description': response.xpath("//meta[@name= 'description']/@content").extract_first().split(',')[1][
                               10:],
                'college': response.xpath("//meta[@name= 'keywords']/@content").extract_first().split(',')[1],
                'summary': ''
                }

        for sum in response.xpath("//div[@class='f-richEditorText']/p/text()").extract():
            item['summary'] += sum.strip()
        script = response.css('script:contains("window.staffLectors")::text').get()

        # print(get)
        # content = re.findall('(?m)^\s*window.staffLectors.*;$(?m)', get)

        # for match in re.finditer('lectorName : "(.*?)"', get):
        #     print(match.group())
        lectors = []
        chiefLector_str = ''.join(re.findall('chiefLector = \\{([^}]*)\\}', script))
        chiefLector_list = re.sub('\s+', '', ' '.join(chiefLector_str.split())).strip()
        chiefLector = demjson.decode("{" + chiefLector_list + "}")
        lectors.append(chiefLector)
        print(re.findall('staffLectors = \\[([^}]*)\\]', script))
        # staffLectors_str = ''.join(re.findall('staffLectors = \\[([^}]*)\\]', script))
        # print(staffLectors_str)
        # lector = {}
        # lectors = []
        # for lector in chiefLector_list:
        #     print(lector.strip().split(':')[1])

        # print(json.dumps(get))
        # print(response.body.decode(response.encoding))
        # all = re.findall('window.staffLectors = (.+);n', get)
        # print(all)
        # pattern = re.compile(r"window.staffLectors = '(.*?)';$")
        # pattern = re.compile("[\u4e00-\u9fa5]")
        # search = pattern.search(response.body.decode(response.encoding))
        # print(search)
        # print(response.body.decode(response.encoding).find('window.chiefLector'))

        # yield item

    def parse_detail(self, response):
        pass
