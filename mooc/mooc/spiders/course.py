import scrapy


class CourseSpider(scrapy.Spider):
    name = 'course'
    allowed_domains = ['course163.org/course']
    start_urls = ['http://course163.org/course/']

    def parse(self, response):
        pass
