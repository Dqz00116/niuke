import re
import datetime
from niuke.db_connecter import DBconnecter
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from lxml import etree


class DataCatcher:
    def __init__(self):
        option = ChromeOptions()
        option.add_argument("--headless")
        self.browser = webdriver.Chrome(options=option)
        print("——虚拟浏览器已启动——")
        self.db = DBconnecter()

    def __del__(self):
        print("——虚拟浏览器已关闭——")
        self.browser.close()
        print("———数据传输完毕——")


    # 获取网页源代码
    def get_page_source(self, target_url):
        self.browser.get(url=target_url)
        page_source = self.browser.page_source
        return page_source

    # 抓取渲染后的页面
    def get_static_html(self, page_source):
        # html数据实例化
        html = etree.HTML(page_source)
        items = html.xpath('.//li[@class="clearfix"]')
        return items

    # 过滤渲染在布局中数据,返回数据列表
    def get_page_data(self, items):
        job_item_list = []
        city_item_list = []
        time_id = self.get_time_id()
        for item in items:
            # 时间id
            time_id += 1
            tid = str(time_id)
            # 岗位信息
            s_job_title = item.xpath('.//a[@class="reco-job-title"]/text()')
            job_title = self.join_list(s_job_title)
            # 公司信息
            s_company = item.xpath('.//div[@class="reco-job-com"]/a/text()')
            company = self.join_list(s_company)
            # 工作地点
            s_job_address = item.xpath('.//span[@class="nk-txt-ellipsis js-nc-title-tips job-address"][1]/text()')
            job_address = self.join_list(s_job_address)
            # 薪资
            s_salary = item.xpath('.//span[@class="ico-nb"]/../text()')
            salary = self.join_list(s_salary)
            # 发布时间
            s_publish_date = item.xpath('.//div[@class="reco-job-detail"]/span[2]/text()')
            publish_date = self.join_list(s_publish_date)
            # 处理率
            s_response_rate = item.xpath('.//span[@class="intern_center js-nc-title-tips"]/text()')
            response_rate = self.join_list(s_response_rate)
            # 平均处理时间
            s_response_time = item.xpath('.//div[@class="reco-job-status"]/span[2]/text()')
            response_time = self.join_list(s_response_time)
            # 处理状态
            s_status = item.xpath('.//div[@class="reco-job-info"]/div[1]/span[3]/text()')
            status = self.join_list(s_status)
            job_item_list.append((
                tid,
                job_title,
                company,
                self.filter_salary(salary),
                self.filter_publish_date(publish_date),
                self.filter_digital(response_rate),
                self.filter_digital(response_time),
                status
            ))
            city_item_list.extend(self.filter_address(tid, job_address))
        list_set = [job_item_list, city_item_list]
        return list_set

    def insert_date_base(self, lists):
        try:
            self.db.commit_job_list(lists[0])
            self.db.commit_city_list(lists[1])
        except IOError:
            print("__error__: Failed to insert_date_base()")

    # 处理列表到字符串
    def join_list(self, item):
        return "".join(item)

    # 生成时间戳
    def get_time_id(self):
        return int('{0:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now()))

    # 过滤SALARY，返回均值
    def filter_salary(self, salary):
        ave_val = 0
        search = re.compile(r'\d+')
        num_list = search.findall(salary)
        if len(num_list) > 1:
            max_num = int(num_list[1])
            min_num = int(num_list[0])
            ave_val = int((max_num + min_num) / 2)
        return ave_val

    # 匹配字符串中的数字，返回整形数，默认返回0，
    def filter_digital(self, text):
        num = 0
        search = re.compile(r'\d+')
        response = search.findall(text)
        if response:
            num = int("".join(response))
        return num

    # 过滤ADDRESS，返回ID-JOB_ADDRESS字典列表
    def filter_address(self, tid, address):
        city_table_item = []
        # 如果地址为空，则默认JOB_ADDRESS为'其他'
        if not address:
            address = "其他"
        # 检测到多个地址，对地址进行分割
        if ',' in address:
            city_set = address.split(',')
            for i_city in city_set:
                city_date_item = (tid, i_city)
                city_table_item.append(city_date_item)
        else:
            city_table_item.append((tid, address))
        return city_table_item

    # 过滤PUBLISH_DATE, 返回小时数
    def filter_publish_date(self, publish_date):
        str_day = '天'
        date = self.filter_digital(publish_date)
        if str_day in publish_date:
            hour = date * 24
        else:
            hour = date
        return hour

   # 打印当前进行的事件
    def show_time(self, event):
        dt_ms = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')  # 含微秒的日期时间，来源 比特量化
        print(dt_ms + ": " + str(event))

    def run(self):
        for page in range(1, 299):
            self.show_time("正在抓取第%d页" % page)
            url_niuke = "https://www.nowcoder.com/intern/center?recruitType=1&page=%d" % page
            page_source = self.get_page_source(url_niuke)
            self.show_time("获取到第%d页的源码" % page)
            items = self.get_static_html(page_source)
            self.show_time("HTML渲染完毕，当前页数: %d" % page)
            date_lists = self.get_page_data(items)
            self.show_time("数据分析完毕，当前页数: %d" % page)
            self.insert_date_base(date_lists)
            self.show_time("成功写入数据库，当前页数: %d，准备抓取下一页……" % page)


if __name__ == '__main__':
    data_catcher_niuke = DataCatcher()
    data_catcher_niuke.run()


