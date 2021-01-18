import scrapy
import re


class CourseSpider(scrapy.Spider):
    name = 'course'
    allowed_domains = ['icourse163.org']
    start_urls = ['https://www.icourse163.org/course/NUDT-42002']

    def parse(self, response):
        item = {'term_id': re.search(r'termId : "(\d+)"', response.text).group(1),
                'title': response.xpath("//meta[@name= 'description']/@content").extract_first().split(',')[0],
                'description': response.xpath("//meta[@name= 'description']/@content").extract_first().split(',')[1][10:],
                'summary': response.xpath("//div[@class='f-richEditorText']/p/text()").extract()
                }
        yield item
