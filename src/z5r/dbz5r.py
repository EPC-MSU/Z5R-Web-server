import datetime
import time

import pymysql
class DbZ5R:
    def __init__(self, host='172.16.131.112',login='z5r', password='Ahthohj0ooJa'):
        self._login = login
        self._password = password
        self._host = host
        self._con = self.db_connect()

    def db_connect(self):
        return pymysql.connect(host=self._host, user=self._login, password=self._password, database='z5r')

    def get_user_names(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute("SELECT Name from DIR_User order by Name")
            rows = cur.fetchall()
            if rows is None:
                return list()
            else:
                return [f"{row[0]}" for row in enumerate(rows, 1)]

    #здесь не хватает карт без пользователя - не умеет mysql делать full join
    #но будут пользователи без карт
    def get_users_cards(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute("SELECT Name, GROUP_CONCAT(DISTINCT CardId ORDER BY CardId SEPARATOR ';') FROM OPT_User_Cards "
                        "RIGHT OUTER JOIN  DIR_Card ON DIR_Card.ID=OPT_User_Cards.ID_Card "
                        "RIGHT OUTER JOIN DIR_User ON DIR_User.ID = OPT_User_Cards.ID_USER "
                        "GROUP BY Name "
                        "ORDER BY Name")
            rows = cur.fetchall()
            if rows is None:
                return list()
            else:
                return [[f"{row[0]}", f"{row[1]}"] for row in rows]

    # получить в виде отдельного набора зарегистрированные карты без пользователей
    def get_cards_registered_free(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute("SELECT CardId from OPT_User_Cards"
                        " RIGHT OUTER JOIN  DIR_Card ON DIR_Card.ID=OPT_User_Cards.ID_Card"
                        " WHERE ISNULL(Id_User) ")

            rows = cur.fetchall()
            if rows is None:
                return list()
            else:
                return [f"{row[0]}" for row in rows]

    def insert_just_card(self, card):
        if card is not None:
            with self._con:
                cur = self._con.cursor()
                #request = 'INSERT IGNORE INTO DIR_Card SET CardId=\'{}\''.format(card)
                card_str = '\'{}\''.format(card)
                request = 'INSERT IGNORE INTO DIR_Card(CardId) VALUES (' + card_str + ')'
                cur.execute(request)
                self._con.commit()
                cur.execute('SELECT ID FROM DIR_Card WHERE CardId=\'{}\''.format(card))
                rows = cur.fetchone()
                return int(f"{rows[0]}")
        else:
            return -1

    def insert_just_user(self, user):
        if user != '':
            with self._con:
                cur = self._con.cursor()
                cur.execute(f'INSERT IGNORE INTO DIR_User SET Name=\'{user}\'')
                self._con.commit()
                cur.execute(f'SELECT ID FROM DIR_User WHERE Name=\'{user}\'')
                rows = cur.fetchone()
                return int(f"{rows[0]}")
        else:
            return -1

    def insert_user_card_list(self, user, card_list):
        id_user = self.insert_just_user(user)
        self._con = self.db_connect()
        id_user_str = '{}'.format(id_user)
        if card_list is not None:
            for card in card_list:
                id_card = self.insert_just_card(card)
                self._con = self.db_connect()
                if id_card !=-1 and id_user != -1:
                    with self._con:
                        cur = self._con.cursor()
                        id_card_str = '{}'.format(id_card)
                        request = f'INSERT IGNORE INTO OPT_User_Cards(ID_User,ID_Card) VALUES({id_user_str},' \
                                  f'{id_card_str})'
                        cur.execute(request)
                        self._con.commit()
                        self._con = self.db_connect()

    def _delete_a_card_user_link(self, card_id):
        with self._con:
            cur = self._con.cursor()
            card_id_str = '{}'.format(card_id)
            cur.execute(f'DELETE IGNORE FROM OPT_User_Cards WHERE ID_Card IN (SELECT ID FROM DIR_Card '
                        f'WHERE ID=\'{card_id_str}\')')
            self._con.commit()

    def _get_user_card_ids(self, user_name):
        with self._con:
            cur = self._con.cursor()
            request = f'SELECT ID_Card FROM OPT_User_Cards WHERE ID_User IN (SELECT ID FROM DIR_User ' \
                      f'WHERE Name=\'{user_name}\')'
            cur.execute(request)
            rows = cur.fetchall()
            if rows is None or rows.count == 0:
                return list()
            else:
                return [f"{row[0]}" for row in enumerate(rows, 1)]

    def get_user_cards(self, user_name):
        with self._con:
            cur = self._con.cursor()
            request = f'SELECT CardId FROM OPT_User_Cards INNER JOIN DIR_Card ON OPT_User_Cards.ID_Card=DIR_Card.ID ' \
                      f'WHERE ID_User IN (SELECT ID FROM DIR_User ' \
                      f'WHERE Name=\'{user_name}\')'
            cur.execute(request)
            rows = cur.fetchall()
            if rows is None or rows.count == 0:
                return list()
            else:
                return [f"{row[0]}" for row in enumerate(rows, 1)]

    def _delete_a_card_totally(self, card_id):
        self._delete_a_card_user_link(card_id)
        self._con = self.db_connect()
        with self._con:
            cur = self._con.cursor()
            card_id_str = '{}'.format(card_id)
            cur.execute(f'DELETE IGNORE FROM DIR_Card WHERE ID=\'{card_id_str}\'')
            self._con.commit()

    def delete_data(self, user_name, card0):
        if user_name != '':
            cards_ids = self._get_user_card_ids(user_name)
            for card_id in cards_ids:
                self._delete_a_card_totally(card_id)
                self._con = self.db_connect()
            cur = self._con.cursor()
            cur.execute(f'DELETE IGNORE FROM DIR_User WHERE Name=\'{user_name}\'')
            self._con.commit()
        # a single card with no user
        elif card0 != '':
            cur = self._con.cursor()
            card_id_str = '{}'.format(card0)
            cur.execute(f'DELETE IGNORE FROM DIR_Card WHERE CardId=\'{card0}\'')
            self._con.commit()

    def get_all_registered_cards(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'SELECT CardId FROM DIR_Cards')
            rows = cur.fetchone()
            if rows is None:
                return list()
            else:
                return [f"{row[0]}" for row in enumerate(rows, 1)]

    def get_all_any_cards_last_10_min(self):
        with self._con:
            cur = self._con.cursor()
            now = datetime.datetime.now()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            ago_10_min = now - datetime.timedelta(hours=0, minutes=10)
            ago_10_min_str = ago_10_min.strftime('%Y-%m-%d %H:%M:%S')
            cur.execute(f'SELECT DISTINCT AnyCardId FROM REG_Event WHERE AnyCardId <> NULL AND AnyCardId <> 0'
                        f' AND DT >= \'{ago_10_min_str}\' AND DT <= \'{now_str}\'')
            rows = cur.fetchone()
            if rows is None:
                return list()
            else:
                return [[f"{row[0]}"] for row in rows]

    def get_reg_user_card_events_per_day(self, time_date, controller_filter=''):
        if controller_filter != '':
            cnt_flt = ' AND Controller={}'.format(controller_filter)
        else:
            cnt_flt = ''
        time_date_str = time_date.timestamp()
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'SELECT DIR_User.Name, MIN(CardId), MIN(DT), MAX(DT) FROM DIR_User INNER JOIN OPT_User_Cards '
                        f'ON DIR_User.ID = OPT_User_Cards.ID_User '
                        f'INNER JOIN DIR_Card ON DIR_Card.ID=OPT_User_Cards.ID_Card INNER JOIN REG_Event ON "'
                        f'DIR_Card.CardId=AnyCardId WHERE DATE(DT)=DATE(\'{time_date_str}\')'
                        f' {cnt_flt} GROUP BY Name ORDER BY Name')
            rows = cur.fetchall()
            if rows is None:
                return list()
            else:
                return [[f"{row[0]}", f"[{row[1]}", f"[{row[2]}", f"[{row[3]}"] for row in enumerate(rows, 1)]

    def get_free_reg_cards_events_per_day(self, time_date, controller_filter=''):
        if controller_filter != '':
            cnt_flt = ' AND Controller={}'.format(controller_filter)
        else:
            cnt_flt = ''
        time_date_str = time_date.timestamp()
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'SELECT CardId, MIN(DT), MAX(DT) FROM DIR_Card INNER JOIN REG_Event ON CardId=AnyCardId '
                        f'WHERE DIR_Card.ID NOT IN (SELECT ID_Card FROM OPT_User_Cards) '
                        f'AND DATE(DT)=DATE(\'{time_date_str}\') {cnt_flt} '
                        f'GROUP BY CardId ORDER BY CardId ')
            rows = cur.fetchall()
            if rows is None:
                return list()
            else:
                return [[f"{row[0]}", f"[{row[1]}", f"[{row[2]}"] for row in enumerate(rows, 1)]

    def get_unregistered_cards_events_per_day(self, time_date, controller_filter=''):
        if controller_filter != '':
            cnt_flt = ' AND Controller={}'.format(controller_filter)
        else:
            cnt_flt = ''
        time_date_str = time_date.timestamp()
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'SELECT AnyCardId, MIN(DT), MAX(DT) FROM REG_Event WHERE AnyCardId NOT IN '
                        f'(SELECT CardId FROM DIR_Card) '
                        f'AND DATE(DT)=DATE(\'{time_date_str}\') {cnt_flt} '
                        f'GROUP BY AnyCardId ORDER BY AnyCardId ')
            rows = cur.fetchall()
            if rows is None:
                return list()
            else:
                return [[f"{row[0]}", f"[{row[1]}", f"[{row[2]}"] for row in enumerate(rows, 1)]


    def insert_an_event(self, time_event, event_id, card, controller, flag):
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'INSERT INTO REG_Event (DT, ID_EventType, AnyCardId,  Controller, Flag) '
                        'SELECT {}, {}, {} ,{}, {})'.format(time_event.timestamp(), event_id, card, controller, flag))
            self._con.commit()


