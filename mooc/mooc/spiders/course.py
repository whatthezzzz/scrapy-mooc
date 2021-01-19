import json

import scrapy
import re
import demjson
from bs4 import BeautifulSoup


class CourseSpider(scrapy.Spider):
    name = 'course'
    allowed_domains = ['icourse163.org']
    start_urls = ['https://www.icourse163.org/course/NUDT-42002']

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
        lectors = []
        chiefLector_str = ''.join(re.findall('chiefLector = \\{([^}]*)\\}', script))
        chiefLector_list = re.sub('\s+', '', ' '.join(chiefLector_str.split())).strip()
        chiefLector = demjson.decode("{" + chiefLector_list + "}")
        lectors.append(chiefLector)
        staffLectors_str = ''.join(re.findall('staffLectors = \[([^\[\]]+)\]', script))
        staffLectors_list = re.sub('\s+', '', ' '.join(staffLectors_str.split())).strip()
        staffLector = demjson.decode("[" + staffLectors_list + "]")
        if staffLector:
            for staff in staffLector:
                lectors.append(staff)
        item['lector'] = lectors

        yield item

    def parse_detail(self, response):
        pass
