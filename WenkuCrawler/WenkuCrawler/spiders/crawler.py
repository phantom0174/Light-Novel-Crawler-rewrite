import os
import scrapy
from opencc import OpenCC


def remove_invalid_characters(target_string):
    return target_string \
        .replace('\\', '_') \
        .replace('/', '_') \
        .replace(':', '：') \
        .replace('*', '＊') \
        .replace('?', '？') \
        .replace('"', '_') \
        .replace('<', '＜') \
        .replace('>', '＞') \
        .replace('|', '｜')


class WenkuCrawler(scrapy.Spider):
    name = 'wenku'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trans = OpenCC('s2tw')

        self.start_urls = [input('Input the url of the book: ')]

        self.domain = ''
        if self.start_urls[0].endswith('m'):
            self.domain = str(self.start_urls[0].split('index')[0])

        self.parse_stage = 'fetch_novel_detail'

        # stage: fetch_novel_detail
        self.novel_name = ''
        self.novel_export_folder = ''
        
        self.book_titles = []
        self.book_chapter_count = []

        self.book_chapter_names = []
        self.book_chapter_links = []

        # stage: fetch_chapter_inner_text
        self.cur_book = 0
        self.cur_chapter = 0

        self.book_chapters_text_buffer = []
        self.main_buffer = []

    def parse(self, response, **kwargs):
        if self.parse_stage == 'fetch_novel_detail':
            self.novel_name = response.xpath('//*[@id="title"]/text()').get()

            row_classes = []

            chapter_names = []
            chapter_links = []

            row_class_links = response.xpath('//td[contains(@class,"css")]')
            for item in row_class_links:
                row_class = item.xpath('@class').get()

                if row_class == 'ccss' and item.xpath('string()').get() != '\xa0':
                    chapter_name = item.xpath('a/text()').extract()[0]
                    if chapter_name[-2:] != '插图' and chapter_name[-2:] != '插圖':
                        row_classes.append(row_class)

                        chapter_names.append(chapter_name)

                        chapter_partial_link = item.css('a::attr(href)').extract()[0]
                        chapter_links.append(self.domain + chapter_partial_link)
                elif row_class == 'vcss':
                    row_classes.append(row_class)

                    book_title = item.xpath('text()').get()
                    self.book_titles.append(book_title)

            row_classes.append('vcss')

            # Find the chapter-count of each book
            # remove the first vcss
            row_classes.remove(row_classes[0])

            chapter_count = 0
            for item in row_classes:
                if item == 'vcss':
                    self.book_chapter_count.append(chapter_count)
                    chapter_count = 0
                else:
                    chapter_count += 1

            if len(chapter_names) != sum(self.book_chapter_count) or len(chapter_links) != sum(self.book_chapter_count):
                print('chapter_names and chapter_count', len(chapter_names), sum(self.book_chapter_count))
                print('chapter_links and chapter_count', len(chapter_links), sum(self.book_chapter_count))
                raise BaseException('ERROR WHEN GROUPING NAMES AND LINKS')

            # Group the names and links by book_chapter_count
            for count in self.book_chapter_count:
                self.book_chapter_names.append(chapter_names[:count])
                self.book_chapter_links.append(chapter_links[:count])

                chapter_names = chapter_names[count:]
                chapter_links = chapter_links[count:]

            # Translation
            self.novel_name = self.trans.convert(self.novel_name)
            self.book_titles = [self.trans.convert(title) for title in self.book_titles]

            for index, item in enumerate(self.book_chapter_names):
                self.book_chapter_names[index] = [self.trans.convert(name) for name in item]

            self.novel_name = remove_invalid_characters(self.novel_name)
            self.book_titles = [remove_invalid_characters(title) for title in self.book_titles]

            self.novel_export_folder = f"D:\\{self.novel_name}"

            self.parse_stage = 'fetch_chapter_inner_text'
        elif self.parse_stage == 'fetch_chapter_inner_text':
            inner_text_links = response.xpath('//*[@id="content"]/text()')
            inner_text = ''.join([content.get() for content in inner_text_links])
            self.book_chapters_text_buffer.append(inner_text)

            if (self.cur_chapter + 1) == self.book_chapter_count[self.cur_book]:
                if (self.cur_book + 1) == len(self.book_titles):
                    self.parse_stage = 'dump_parsed_data'

                self.main_buffer.append(self.book_chapters_text_buffer.copy())
                self.book_chapters_text_buffer.clear()
                self.cur_book += 1
                self.cur_chapter = 0

            else:
                self.cur_chapter += 1

        if self.parse_stage == 'dump_parsed_data':
            if not os.path.isdir(self.novel_export_folder):
                os.mkdir(self.novel_export_folder)

            for book_index, book_title in enumerate(self.book_titles):
                txt_path = f"{self.novel_export_folder}\\{book_index + 1}{book_title}.txt"

                with open(txt_path, 'w', encoding='utf-8') as file:
                    for chapter_index, chapter_contents in enumerate(self.main_buffer[book_index]):
                        chapter_prefix = f"//{self.book_chapter_names[book_index][chapter_index]}"
                        file.write(chapter_prefix)

                        for content in chapter_contents:
                            file.write(self.trans.convert(content))

        if self.parse_stage == 'fetch_chapter_inner_text':
            yield scrapy.Request(url=self.book_chapter_links[self.cur_book][self.cur_chapter], callback=self.parse)
