import pymysql
from twisted.enterprise import adbapi


class MysqlPipelineTwo(object):
    def __init__(self, dbpool):
        print("__init__", "__init__")
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
        """
        数据库建立连接
        :param settings: 配置参数
        :return: 实例化参数
        """
        adbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
        )
        # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
        dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
        print("adbparams", adbparams)
        # 返回实例化参数
        return cls(dbpool)

    def process_item(self, item, spider):
        print("process_item", "process_item")
        query = self.dbpool.runInteraction(self.do_insert, item)  # 指定操作方法和操作数据
        # 添加异常处理
        query.addCallback(self.handle_error)  # 处理异常

    def do_insert(self, cursor, item):
        print("即将入库是信息",item)
        # 对数据库进行插入操作，并不需要commit，twisted会自动commit
        insert_sql = """
        insert into wordpress.wp_posts ( post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status, comment_status, ping_status, post_password, post_name, to_ping, pinged, post_modified, post_modified_gmt, post_content_filtered, post_parent, guid, menu_order, post_type, post_mime_type, comment_count) VALUES ( 1, '2019-09-18 16:06:53', '2019-09-18 08:06:53', %s, %s, '', 'publish', 'open', 'open', '', '', '', '', '2019-09-18 16:06:53', '2019-09-18 08:06:53', '', 0, '', 0, 'post', '', 0);
                    """
        cursor.execute(insert_sql, (item['content'], item['title']))

    def handle_error(self, failure):
        print("handle_error", failure)
        if failure:
            # 打印错误信息
            print(failure)