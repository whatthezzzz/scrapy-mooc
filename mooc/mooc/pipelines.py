# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import urllib.request
from itemadapter import ItemAdapter
import time
import json
from collections import defaultdict
from .utils import *
from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"
MONGO_DB = "mooc_spider"
MONGO_TABLE = "course"
client = MongoClient(MONGO_URL)
db = client[MONGO_DB]

outline = {}
play_list = []
subtitles = []
WORK_DIR = ''

def save_to_mongo(data):
    if db[MONGO_TABLE].insert(data):
        print("SAVE SUCCESS", data)
        return True
    return False


def parse_resource(resource):
    post_data = {'callCount': '1', 'scriptSessionId': '${scriptSessionId}190',
                 'httpSessionId': '5531d06316b34b9486a6891710115ebc', 'c0-scriptName': 'CourseBean',
                 'c0-methodName': 'getLessonUnitLearnVo', 'c0-id': '0', 'c0-param0': 'number:' + resource[0],
                 'c0-param1': 'number:' + resource[1], 'c0-param2': 'number:0',
                 'c0-param3': 'number:' + resource[2], 'batchId': str(int(time.time()) * 1000)}
    res = requests.post('https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr',
                        params=post_data).text

    file_name = resource[3]
    index = file_name.find(".")
    if index != -1:
        file_name = file_name.replace(".", "-")

    resolutions = ['Shd', 'Hd', 'Sd']
    play_info = {}
    for sp in resolutions:
        video_info = re.search(r'(?P<ext>mp4)%sUrl="(?P<url>.*?\.(?P=ext).*?)"' % sp, res)

        if video_info:
            url, ext = video_info.group('url', 'ext')
            ext = '.' + ext
            play_info['name'] = file_name
            play_info['video_url'] = url

            # print("downloading with urllib")
            # f = urllib.request.urlopen(url)
            # data = f.read()
            # with open("H:\\test\\" + file_name + ext, "wb") as code:
            #     code.write(data)
            #
            # if not os.path.exists(data_path + r'\\' + attachment_name):
            #     with open(data_path + r'\\' + attachment_name, 'wb')as f:
            #         f.write(response.body)
            break




    subtitles = re.findall(r'name="(.+)";.*url="(.*?)"', res)
    for subtitle in subtitles:
        if len(subtitles) == 1:
            sub_name = file_name + '.srt'

        else:
            subtitle_lang = subtitle[0].encode('utf_8').decode('unicode_escape')
            sub_name = file_name + '_' + subtitle_lang + '.srt'

        play_info['sub_url'] = subtitle[1]
    play_list.append(play_info)


def get_resource(term_id):
    counter = Counter()
    CONFIG = {}
    pdf_list = []
    video_list = []
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

            # 视频
            videos = re.findall(r'contentId=(\d+).+contentType=(1).+id=(\d+).+lessonId=' +
                                lesson[0] + r'.+name="(.+)"', res)

            for video in videos:
                counter.add(2)
                parse_resource(video)
                video_list.append(video[3])
            # print(video_list)

            # 课件
            pdfs = re.findall(r'contentId=(\d+).+contentType=(3).+id=(\d+).+lessonId=' +
                              lesson[0] + r'.+name="(.+)"', res)
            for pdf in pdfs:
                counter.add(2)


class MoocPipeline:
    def __init__(self):
        pass

    def process_item(self, item, spider):
        if spider.name == 'course':
            get_resource(item["term_id"])
        else:
            return
        item['outline'] = outline
        item['play_list'] = play_list
        save_to_mongo(item)
        return item
