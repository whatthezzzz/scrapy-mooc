import wget
import logging
from itemadapter import ItemAdapter
import time
import json
from collections import defaultdict
from .utils import *
from pymongo import MongoClient


class MoocPipeline:
    data_path = 'H:/course/'
    MONGO_URL = "mongodb://10.215.42.31:27017"
    MONGO_DB = "mooc_spider"
    MONGO_TABLE = "course"

    client = MongoClient(MONGO_URL)
    db = client[MONGO_DB]

    outline = {}
    play_list = []
    subtitles = []
    WORK_DIR = ''

    def parse_resource(self, resource, counter):
        post_data = {'callCount': '1', 'scriptSessionId': '${scriptSessionId}190',
                     'httpSessionId': '5531d06316b34b9486a6891710115ebc', 'c0-scriptName': 'CourseBean',
                     'c0-methodName': 'getLessonUnitLearnVo', 'c0-id': '0', 'c0-param0': 'number:' + resource[0],
                     'c0-param1': 'number:' + resource[1], 'c0-param2': 'number:0',
                     'c0-param3': 'number:' + resource[2], 'batchId': str(int(time.time()) * 1000)}
        res = requests.post('https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr',
                            params=post_data).text
        file_name = resource[3].strip()
        index_dunhao = file_name.find("、")
        if index_dunhao != -1:
            file_name = "{}{}".format(counter, file_name.split("、")[1])
        else:
            file_name = "{}{}".format(counter, file_name)
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

                logging.info("正在下载： {} ".format(file_name + ext))
                try:
                    r = requests.get(url)
                    if not os.path.exists(self.data_path + r'\video\\' + file_name + ext):
                        with open(self.data_path + r'\video\\' + file_name + ext, 'wb')as f:
                            f.write(r.content)
                    play_info['video_path'] = self.data_path + r'\video\\' + file_name + ext
                    logging.info("下载成功！")
                    break
                except Exception as e:
                    logger.erro("下载失败：{}  {}".format(file_name, url), e)

        subtitles = re.findall(r'name="(.+)";.*url="(.*?)"', res)
        for subtitle in subtitles:
            if len(subtitles) == 1:
                sub_name = file_name + '.srt'
            else:
                subtitle_lang = subtitle[0].encode('utf_8').decode('unicode_escape')
                sub_name = file_name + '_' + subtitle_lang + '.srt'

            try:
                r = requests.get(subtitle[1])
                play_info['sub_url'] = subtitle[1]
                if not os.path.exists(self.data_path + r'\video\\' + sub_name):
                    with open(self.data_path + r'\video\\' + sub_name, 'wb')as f:
                        f.write(r.content)
                play_info['sub_path'] = self.data_path + r'\video\\' + sub_name
                logging.info("下载成功！")
            except Exception as e:
                logger.erro("下载失败：{}  {}".format(sub_name, subtitle[1]), e)




        self.play_list.append(play_info)

    def save_to_mongo(self, data):
        if self.db[self.MONGO_TABLE].insert(data):
            print("SAVE SUCCESS", data)
            return True
        return False

    def __init__(self):
        pass

    def get_resource(self, term_id):
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
                self.outline[chapter[1]] = lesson_list

                # 视频
                videos = re.findall(r'contentId=(\d+).+contentType=(1).+id=(\d+).+lessonId=' +
                                    lesson[0] + r'.+name="(.+)"', res)
                for video in videos:
                    counter.add(2)
                    if video:
                        try:
                            os.mkdir(self.data_path + r'\video')
                        except FileExistsError:
                            pass
                        self.parse_resource(video, counter)
                    video_list.append(video[3])

                # 课件
                pdfs = re.findall(r'contentId=(\d+).+contentType=(3).+id=(\d+).+lessonId=' +
                                  lesson[0] + r'.+name="(.+)"', res)
                for pdf in pdfs:
                    counter.add(2)

    def process_item(self, item, spider):
        if spider.name == 'course':
            self.data_path = os.path.join(self.data_path, item['title'])
            try:
                os.mkdir(self.data_path)
            except FileExistsError:
                pass
            self.get_resource(item["term_id"])
        else:
            return

        item['outline'] = self.outline
        item['play_list'] = self.play_list
        self.save_to_mongo(item)
        return item
