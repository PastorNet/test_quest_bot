import sqlite3 as sql
import datetime


def logging(func):
    def wrapper(*args, **kwargs):

        # try:
            func(*args, **kwargs)

        # except sql.DataError as e:
        #     DbController.errlog = e
        # except sql.DatabaseError as e:
        #     DbController.errlog = e
        # except sql.Error as e:
        #     DbController.errlog = e

    return wrapper


class DbController:

    def __init__(self, db_name: str):
        self.__name = db_name
        self.__con = sql.connect(db_name)
        self.__cur = self.__con.cursor()
        self.__response_state = {}
        self.__errlog = []
        self.__last_update_date = datetime.datetime.now()
        self.__inited = False
        self.__created = False
        self.__cur.execute("CREATE TABLE IF NOT EXISTS `rates`( `rate_key` TEXT, `rate_value` REAL) ")
        self.__con.commit()

    @logging
    def insert(self, data: dict):
        keys = list(data.keys())
        prepared_data = [
            (keys[i], data.get(keys[i])) for i in range(0, len(keys))
        ]
        self.__cur.executemany("INSERT INTO `rates` VALUES (?,?)", prepared_data)
        self.__con.commit()
        self.last_update_date = datetime.datetime.now()
        self.__inited = True

    @logging
    def update(self, data: dict):
        keys = list(data.keys())
        prepared_data = [
            (data.get(keys[i]),keys[i],) for i in range(0, len(keys))
        ]
        self.__cur.executemany("UPDATE `rates`  SET `rate_value`= ? WHERE `rate_key` = ?", prepared_data)
        self.__con.commit()
        self.last_update_date = datetime.datetime.now()

    @logging
    def select(self, key=''):
        response = {}

        if key:
            quary = "SELECT * FROM `rates` WHERE `rate_key` = ?"
            db_response = self.__cur.execute(quary,(key,)).fetchall()

        else:
            quary = f"SELECT * FROM `rates`"
            db_response = self.__cur.execute(quary).fetchall()

        for x in db_response:
            key, value = x
            response[key] = value
        self.response_state = response
        self.__con.commit()

    @property
    def response_state(self):
        return self.__response_state

    @response_state.setter
    def response_state(self, value):
        self.__response_state = value

    @property
    def errlog(self):
        return self.__errlog

    @errlog.setter
    def errlog(self, value):
        self.__errlog.append(value)

    @property
    def last_update_date(self):
        return self.__last_update_date

    @last_update_date.setter
    def last_update_date(self, date):
        self.__last_update_date = date

    @property
    def inited(self):
        return self.__inited

    @logging
    def close(self):
        self.__con.close()
