import datetime
import configparser
import pymysql


# the global vars
ini_has_read = False
ini_host = ''
ini_db = ''
ini_login = ''
ini_password = ''


class DbZ5R:
    def __init__(self):
        self.read_ini()
        self._login = ini_login
        self._password = ini_password
        self._host = ini_host
        self._db = ini_db
        self._con = None

    @staticmethod
    def read_ini():
        global ini_password, ini_has_read, ini_login, ini_host, ini_db
        if not ini_has_read:
            ini_has_read = True
            config = configparser.ConfigParser()
            config.read('service_data/z5r.ini')
            ini_host = config['Db_Connection']['host']
            ini_db = config.get('Db_Connection', 'db')
            ini_login = config.get('Db_Connection', 'login')
            ini_password = config.get('Db_Connection', 'password')

    def set_test_db_name(self):
        self._db += '_test'

    def db_connect(self):
        self._con = pymysql.connect(host=self._host, user=self._login, password=self._password, database=self._db)

    def db_check_create_db_schema(self):
        self._con = pymysql.connect(host=self._host, user=self._login, password=self._password)
        cursor = self._con.cursor()
        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self._db}')
        self._con.commit()
        self.db_connect()
        # check and create tables now
        cursor = self._con.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS CLS_EventType ('
                       'ID int primary key, Name varchar(255) not null)')
        self._con.commit()
        self.db_connect()
        cursor = self._con.cursor()
        cursor.execute('INSERT IGNORE INTO CLS_EventType (ID, Name)'
                       '(select 0, \'Opened from inside on entrance\') union'
                       '(select 1, \'Opened from inside on exit\') union'
                       '(select 2, \'Key not in database on entrance\') union'
                       '(select 3, \'Key not in database on exit\') union'
                       '(select 4, \'Key in database, door opened on entrance\') union'
                       '(select 5, \'Key in database, door opened on exit\') union'
                       '(select 6, \'Key in database, access denied on entrance\') union'
                       '(select 7, \'Key in database, access denied on exit\') union'
                       '(select 8, \'Door opened from network on entrance\') union'
                       '(select 9, \'Door opened from network on exit\') union'
                       '(select 10, \'Key in database, door locked on entrance\') union'
                       '(select 11, \'Key in database, door locked on exit\') union'
                       '(select 12, \'Door violation on entrance\') union'
                       '(select 13, \'Door violation on exit\') union'
                       '(select 14, \'Door kept open timeout on entrance\') union'
                       '(select 15, \'Door kept open timeout on exit\') union'
                       '(select 16, \'Passed on entrance\') union'
                       '(select 17, \'Passed on exit\') union'
                       '(select 20, \'Controller reboot\') union'
                       '(select 21, \'Power (see flag)\') union'
                       '(select 32, \'Door opened on entrance\') union'
                       '(select 33, \'Door opened on exit\') union'
                       '(select 34, \'Door closed on entrance\') union'
                       '(select 35, \'Door closed on exit\') union'
                       '(select 37, \'Mode changed (see flags)\') union'
                       '(select 38, \'Controller on fire (see flags)\') union'
                       '(select 39, \'Security event (see flags)\') union'
                       '(select 40, \'No passage during grace period on entrance\') union'
                       '(select 41, \'No passage during grace period on exit\') union'
                       '(select 48, \'Gateway is entered on entrance\') union'
                       '(select 49, \'Gateway is entered on exit\') union'
                       '(select 50, \'Gateway blocked on entrance\') union'
                       '(select 51, \'Gateway blocked on exit\') union'
                       '(select 52, \'Gateway enterance allowed on entrance\') union'
                       '(select 53, \'Gateway enterance allowed on exit\') union'
                       '(select 54, \'Passage blocked on entrance\') union'
                       '(select 55, \'Passage blocked on exit\')')

        self._con.commit()
        self.db_connect()
        cursor.execute('CREATE TABLE IF NOT EXISTS DIR_User('
                       'ID int auto_increment primary key, '
                       'Name varchar(255) not null UNIQUE)')
        self._con.commit()
        self.db_connect()
        cursor.execute('CREATE TABLE IF NOT EXISTS DIR_Card('
                       'ID int auto_increment primary key, '
                       'CardId int not null UNIQUE)')
        self._con.commit()
        self.db_connect()
        cursor.execute('CREATE TABLE IF NOT EXISTS OPT_User_Cards('
                       'ID int auto_increment primary key, '
                       'ID_User int not null, '
                       'ID_Card int not  null unique, '
                       'foreign key(ID_User) '
                       'references DIR_User(ID), '
                       'foreign key (ID_Card) '
                       'references DIR_Card(ID), '
                       'unique key ID_User_Card (ID_User, ID_Card))')
        self._con.commit()
        self.db_connect()
        cursor.execute('CREATE TABLE IF NOT EXISTS REG_Event ('
                       'ID int auto_increment primary key, '
                       'DT datetime not null, '
                       'ID_EventType int not null, '
                       'Text varchar(1024) null, '
                       'AnyCardId int null, '
                       'Controller varchar(128) null, '
                       'Flag int null, '
                       'foreign key(ID_EventType) '
                       'references CLS_EventType(ID))')

    def check_db_connection(self):
        try:
            self.db_connect()
            self._con.cursor()
        except pymysql.OperationalError:
            return False
        return True

    def get_user_names(self):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute("SELECT Name from DIR_User order by Name")
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [f"{row[1][0]}" for row in enumerate(rows, 1)]

    def get_user_time(self, name, dt1, dt2):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute(f'SELECT DATE(DT), MIN(DT), MAX(DT) FROM DIR_User '
                           f'INNER JOIN OPT_User_Cards ON DIR_User.ID = OPT_User_Cards.ID_User '
                           f'INNER JOIN DIR_Card ON DIR_Card.ID=OPT_User_Cards.ID_Card INNER JOIN REG_Event ON '
                           f'DIR_Card.CardId=AnyCardId WHERE DATE(DT)>=DATE(\'{dt1}\') AND DATE(DT)<=DATE(\'{dt2}\') '
                           f'AND DIR_User.Name =\'{name}\' '
                           f'GROUP BY DATE(DT) '
                           f'ORDER BY DATE(DT) ')
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [[f"{row[1][0]}", f"{row[1][1]}", f"{row[1][2]}"] for row in enumerate(rows, 1)]

    # no full join in mysql
    def get_users_cards(self):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute("SELECT Name, GROUP_CONCAT(DISTINCT CardId ORDER BY CardId SEPARATOR ';') "
                           "FROM OPT_User_Cards "
                           "RIGHT OUTER JOIN  DIR_Card ON DIR_Card.ID=OPT_User_Cards.ID_Card "
                           "RIGHT OUTER JOIN DIR_User ON DIR_User.ID = OPT_User_Cards.ID_USER "
                           "GROUP BY Name ORDER BY Name")
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [[f"{row[0]}", f"{row[1]}"] for row in rows]

    # get registered cards with no users connected
    def get_cards_registered_free(self):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute("SELECT CardId from OPT_User_Cards"
                           " RIGHT OUTER JOIN  DIR_Card ON DIR_Card.ID=OPT_User_Cards.ID_Card"
                           " WHERE ISNULL(Id_User) ")

            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [f"{row[0]}" for row in rows]

    def insert_just_card(self, card):
        self.db_connect()
        if card is not None:
            with self._con:
                cursor = self._con.cursor()
                card_str = '\'{}\''.format(card)
                request = 'INSERT IGNORE INTO DIR_Card(CardId) VALUES (' + card_str + ')'
                cursor.execute(request)
                self._con.commit()
                cursor.execute('SELECT ID FROM DIR_Card WHERE CardId=\'{}\''.format(card))
                rows = cursor.fetchone()
                return int(f"{rows[0]}")
        else:
            return -1

    def insert_just_user(self, user):
        self.db_connect()
        if user != '':
            with self._con:
                cursor = self._con.cursor()
                cursor.execute(f'INSERT IGNORE INTO DIR_User SET Name=\'{user}\'')
                self._con.commit()
                cursor.execute(f'SELECT ID FROM DIR_User WHERE Name=\'{user}\'')
                rows = cursor.fetchone()
                return int(f"{rows[0]}")
        else:
            return -1

    def insert_user_card_list(self, user, card_list):
        id_user = self.insert_just_user(user)
        id_user_str = '{}'.format(id_user)
        if card_list is not None:
            for card in card_list:
                id_card = self.insert_just_card(card)
                if id_card != -1 and id_user != -1:
                    self.db_connect()
                    with self._con:
                        cursor = self._con.cursor()
                        id_card_str = '{}'.format(id_card)
                        request = f'INSERT IGNORE INTO OPT_User_Cards(ID_User,ID_Card) VALUES({id_user_str},' \
                                  f'{id_card_str})'
                        cursor.execute(request)
                        self._con.commit()

    def _delete_a_card_user_link(self, card_id):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute(f'DELETE IGNORE FROM OPT_User_Cards WHERE ID_Card={card_id}')
            self._con.commit()

    def _get_user_card_ids(self, user_name):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            request = f'SELECT ID_Card FROM OPT_User_Cards WHERE ID_User IN (SELECT ID FROM DIR_User ' \
                      f'WHERE Name=\'{user_name}\')'
            cursor.execute(request)
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [f"{row[1][0]}" for row in enumerate(rows, 1)]

    def get_user_cards(self, user_name):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            request = f'SELECT CardId FROM OPT_User_Cards INNER JOIN DIR_Card ON OPT_User_Cards.ID_Card=DIR_Card.ID ' \
                      f'WHERE ID_User IN (SELECT ID FROM DIR_User ' \
                      f'WHERE Name=\'{user_name}\')'
            cursor.execute(request)
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [f"{row[1][0]}" for row in enumerate(rows, 1)]

    def _delete_a_card_totally(self, card_id):
        self._delete_a_card_user_link(card_id)
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute(f'DELETE IGNORE FROM DIR_Card WHERE ID={card_id}')
            self._con.commit()

    def delete_data(self, user_name, card0):
        if user_name != '':
            cards_ids = self._get_user_card_ids(user_name)
            if len(cards_ids) != 0:
                for card_id in cards_ids:
                    self._delete_a_card_totally(card_id)
            self.db_connect()
            with self._con:
                cursor = self._con.cursor()
                cursor.execute(f'DELETE IGNORE FROM DIR_User WHERE Name=\'{user_name}\'')
                self._con.commit()
        # a single card with no user
        elif card0 != '':
            self.db_connect()
            with self._con:
                cursor = self._con.cursor()
                cursor.execute(f'DELETE IGNORE FROM DIR_Card WHERE CardId={card0}')
                self._con.commit()

    def get_all_registered_cards(self):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute('SELECT CardId FROM DIR_Card')
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [f"{'{:012X}'.format(row[1][0])}" for row in enumerate(rows, 1)]

    def get_non_registered_cards_last_10_min(self):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            now = datetime.datetime.now()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            ago_10_min = now - datetime.timedelta(hours=0, minutes=10)
            ago_10_min_str = ago_10_min.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f'SELECT DISTINCT AnyCardId FROM REG_Event WHERE NOT ISNULL(AnyCardId) AND AnyCardId <> 0'
                           f' AND DT >= \'{ago_10_min_str}\' AND DT <= \'{now_str}\' AND AnyCardId NOT IN '
                           f'(SELECT CardId FROM DIR_Card)')
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [f"{'{:012X}'.format(row[1][0])}" for row in enumerate(rows, 1)]

    def get_reg_user_card_events_per_day(self, time_date):
        time_date_str = time_date.strftime('%Y-%m-%d %H:%M:%S')
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()

            cursor.execute(f'SELECT DIR_User.Name, MIN(CardId), MIN(DT), MAX(DT) FROM DIR_User '
                           f'INNER JOIN OPT_User_Cards ON DIR_User.ID = OPT_User_Cards.ID_User '
                           f'INNER JOIN DIR_Card ON DIR_Card.ID=OPT_User_Cards.ID_Card INNER JOIN REG_Event ON '
                           f'DIR_Card.CardId=AnyCardId WHERE DATE(DT)=DATE(\'{time_date_str}\') '
                           f'GROUP BY Name ORDER BY Name')

            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                ret_list = list()
                for row in enumerate(rows, 1):
                    name = row[1][0]
                    card = '{:012X}'.format(row[1][1])
                    min_dt = row[1][2].strftime('%H:%M:%S')
                    max_dt = row[1][3].strftime('%H:%M:%S')
                    ret_list.append([name, card, min_dt, max_dt])
                return ret_list

    def get_free_reg_cards_events_per_day(self, time_date):
        time_date_str = time_date.strftime('%Y-%m-%d %H:%M:%S')
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute(f'SELECT CardId, MIN(DT), MAX(DT) FROM DIR_Card INNER JOIN REG_Event ON CardId=AnyCardId '
                           f'WHERE DIR_Card.ID NOT IN (SELECT ID_Card FROM OPT_User_Cards) '
                           f'AND DATE(DT)=DATE(\'{time_date_str}\') '
                           f'GROUP BY CardId ORDER BY CardId ')
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                ret_list = list()
                for row in enumerate(rows, 1):
                    card = '{:012X}'.format(row[1][0])
                    min_dt = row[1][1].strftime('%H:%M:%S')
                    max_dt = row[1][2].strftime('%H:%M:%S')
                    ret_list.append([card, min_dt, max_dt])
                return ret_list

    def get_unregistered_cards_events_per_day(self, time_date):
        time_date_str = time_date.strftime('%Y-%m-%d %H:%M:%S')
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute(f'SELECT AnyCardId, MIN(DT), MAX(DT) FROM REG_Event WHERE  NOT ISNULL(AnyCardId) '
                           f'AND AnyCardId <> 0 AND AnyCardId NOT IN (SELECT CardId FROM DIR_Card) '
                           f'AND DATE(DT)=DATE(\'{time_date_str}\') '
                           f'GROUP BY AnyCardId ORDER BY AnyCardId')
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return list()
            else:
                ret_list = list()
                for row in enumerate(rows, 1):
                    card = '{:012X}'.format(row[1][0])
                    min_dt = row[1][1].strftime('%H:%M:%S')
                    max_dt = row[1][2].strftime('%H:%M:%S')
                    ret_list.append([card, min_dt, max_dt])
                return ret_list

    def get_any_events_per_day(self, time_date, controller_sn):
        cnt_flt = ' AND Controller={}'.format(controller_sn)
        time_date_str = time_date.strftime('%Y-%m-%d %H:%M:%S')
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute(f'SELECT DT, AnyCardId, Name FROM REG_Event '
                           f'RIGHT OUTER JOIN CLS_EventType on ID_EventType=CLS_EventType.ID '
                           f'WHERE DATE(DT)=DATE(\'{time_date_str}\') {cnt_flt} '
                           f'ORDER BY DT')
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                ret_list = list()
                for row in enumerate(rows, 1):
                    dt = row[1][0].strftime('%H:%M:%S')
                    card = '{:012X}'.format(row[1][1])
                    name = row[1][2]
                    ret_list.append([dt, card, name])
                return ret_list

    def get_event_type_desc(self, event_id):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute(f'SELECT Name FROM CLS_EventType '
                           f'WHERE ID={str(event_id)}')
            row = cursor.fetchone()
            if row is None or len(row) == 0:
                return ''
            else:
                return f"{row[0]}"

    def insert_events(self, events):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.executemany("INSERT IGNORE INTO REG_Event (DT, ID_EventType, AnyCardId,  Controller, Flag) "
                               "VALUES(%s, %s, %s, %s, %s)", events)
            self._con.commit()


def check_dbz5r_connection():
    dbcon = DbZ5R()
    return dbcon.check_db_connection()


def check_create_db_z5r():
    try:
        dbcon = DbZ5R()
        dbcon.db_check_create_db_schema()
    except pymysql.OperationalError:
        return False
    except Exception:
        return False
    return True
