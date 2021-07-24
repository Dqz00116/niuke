import pymysql


class DBconnecter(object):
    def __init__(self):
        # 连接数据库
        self.db = pymysql.connect(
            host='localhost',
            user='',
            password='',
            database='db_niuke',
        )
        print("——数据库连接成功——")
        # 游标
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()
        print("——数据库连接关闭——")

    # 插入岗位信息
    def commit_job_list(self, job_list):
        sql = "INSERT INTO JOB_DATA ( ID, JOB_TITLE, COMPANY, AVE_SALARY, PUBLISH_DATE, " \
              "RESPONSE_RATE, RESPONSE_TIME, RESPONSE_STATUS ) " \
              "VALUES( %s, %s, %s, %s, %s, %s, %s, %s );"
        self.cursor.executemany(sql, job_list)
        self.db.commit()

    # 插入城市信息
    def commit_city_list(self, city_list):
        sql = "INSERT INTO CITY_DATA(ID, JOB_ADDRESS) VALUES (%s, %s)"
        self.cursor.executemany(sql, city_list)
        self.db.commit()
