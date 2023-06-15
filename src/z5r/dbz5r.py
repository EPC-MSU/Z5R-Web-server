import datetime
import time

import pymysql
class DbZ5R:
    def __init__(self, host='172.16.131.112',login='z5r', password='Ahthohj0ooJa'):
        self._login = login
        self._password = password
        self._host = host
        self._con = None

    def db_connect(self):
        self._con = pymysql.connect(host=self._host, user=self._login, password=self._password, database='z5r')

    def get_user_names(self):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute("SELECT Name from DIR_User order by Name")
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [f"{row[0]}" for row in enumerate(rows, 0)]

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
                if id_card !=-1 and id_user != -1:
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
            card_id_str = '{}'.format(card_id)
            cursor.execute(f'DELETE IGNORE FROM OPT_User_Cards WHERE ID_Card IN (SELECT ID FROM DIR_Card '
                           f'WHERE ID=\'{card_id_str}\')')
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
                return [[f"{row[1][0]}"] for row in enumerate(rows, 1)]

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
                return [[f"{row[1][0]}"] for row in enumerate(rows, 1)]

    def _delete_a_card_totally(self, card_id):
        self._delete_a_card_user_link(card_id)
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            card_id_str = '{}'.format(card_id)
            cursor.execute(f'DELETE IGNORE FROM DIR_Card WHERE ID=\'{card_id_str}\'')
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
                card_id_str = '{}'.format(card0)
                cursor.execute(f'DELETE IGNORE FROM DIR_Card WHERE CardId=\'{card0}\'')
                self._con.commit()

    def get_all_registered_cards(self):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            cursor.execute(f'SELECT CardId FROM DIR_Cards')
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [f"{row[0]}" for row in enumerate(rows, 1)]

    def get_all_any_cards_last_10_min(self):
        self.db_connect()
        with self._con:
            cursor = self._con.cursor()
            now = datetime.datetime.now()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            ago_10_min = now - datetime.timedelta(hours=0, minutes=10)
            ago_10_min_str = ago_10_min.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f'SELECT DISTINCT AnyCardId FROM REG_Event WHERE AnyCardId <> NULL AND AnyCardId <> 0'
                           f' AND DT >= \'{ago_10_min_str}\' AND DT <= \'{now_str}\'')
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [[f"{row[0]}"] for row in rows]

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
            cursor.execute(f'SELECT AnyCardId, MIN(DT), MAX(DT) FROM REG_Event WHERE AnyCardId NOT IN '
                           f'(SELECT CardId FROM DIR_Card) '
                           f'AND DATE(DT)=DATE(\'{time_date_str}\') '
                           f'GROUP BY AnyCardId ORDER BY AnyCardId ')
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
                           f'GROUP BY AnyCardId ORDER BY DT')
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return list()
            else:
                return [[f"{row[0].strftime('%H:%M:%S')}", f"{'{:012X}'.format(row[1])}", f"{row[2]}"] for row in rows]

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
            cursor.executemany("""INSERT IGNORE INTO REG_Event (DT, ID_EventType, AnyCardId,  Controller, Flag) "
                               "VALUES(%s, %s, %s, %s, %s)""", events)
            self._con.commit()


