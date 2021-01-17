# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import time
import json
from collections import defaultdict
from .utils import *

outline = {}


def get_resource(term_id):
    counter = Counter()
    video_list = []
    pdf_list = []
    rich_text_list = []
    post_data = {'callCount': '1', 'scriptSessionId': '${scriptSessionId}190', 'c0-scriptName': 'CourseBean',
                 'c0-methodName': 'getMocTermDto', 'c0-id': '0', 'c0-param0': 'number:' + term_id,
                 'c0-param1': 'number:0', 'c0-param2': 'boolean:true', 'batchId': str(int(time.time()) * 1000)}
    res = requests.post('https://www.icourse163.org/dwr/call/plaincall/CourseBean.getMocTermDto.dwr',
                        params=post_data).text.encode('utf_8').decode('unicode_escape')

    chapters = re.findall(r'homeworks=\w+;.+id=(\d+).+name="(.+)";', res)
    for chapter in chapters:
        counter.add(0)
        lessons = re.findall(r'chapterId=' + chapter[0] + r'.+contentType=1.+id=(\d+).+name="(.+)".+test', res)

        lesson_list = []
        for lesson in lessons:
            counter.add(1)

            lesson_list.append(lesson[1])
            outline[chapter[1]] = lesson_list

            videos = re.findall(r'contentId=(\d+).+contentType=(1).+id=(\d+).+lessonId=' +
                                lesson[0] + r'.+name="(.+)"', res)


            video_list = []
            for video in videos:
                counter.add(2)
                video_list.append(video[3])
            # print(video_list)

            # 课件
            pdfs = re.findall(r'contentId=(\d+).+contentType=(3).+id=(\d+).+lessonId=' +
                              lesson[0] + r'.+name="(.+)"', res)
            # for pdf in pdfs:
            #     print(pdf[3])


    # outline.write(chapter[1], counter, 0)
    # lessons = re.findall(r'chapterId=' + chapter[0] + r'.+contentType=1.+id=(\d+).+name="(.+)".+test', res)
    # print(lessons)

    pass


class MoocPipeline:
    def process_item(self, item, spider):
        if spider.name == 'course':
            get_resource(item["term_id"])

        item['outline'] = outline

        return item
