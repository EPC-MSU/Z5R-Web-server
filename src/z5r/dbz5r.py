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
            return [f"row[0]" for row in enumerate(rows, 1)]

    #здесь не хватает карт без пользователя - не умеет mysql лелать full join
    #но будут пользователи без карт
    def get_users_cards(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute("SELECT Name, GROUP_CONCAT(DISTINCT CardId ORDER BY CardId SEPARATOR ',') FROM OPT_User_Cards "
                        "RIGHT OUTER JOIN  DIR_Card ON DIR_Card.ID=OPT_User_Cards.ID_Card "
                        "RIGHT OUTER JOIN DIR_User ON DIR_User.ID = OPT_User_Cards.ID_USER"
                        "GROUP BY Name"
                        "ORDER BY Name")
            rows = cur.fetchall()
            return [[f"row[0]", f"[row[1]"] for row in enumerate(rows, 1)]

    def insert_just_card(self, card):
        if card != '':
            with self._con:
                cur = self._con.cursor()
                int_card = int(card)
                cur.execute(f'INSERT IGNORE INTO DIR_Card SET CardId=\'{int_card}\'')
                cur.execute(f'SELECT ID FROM DIR_Card WHERE CardId=\'{int_card}\'')
                rows = cur.fetchall()
                return rows[0]
        else:
            return -1

    def insert_just_user(self, user):
        if user != '':
            with self._con:
                cur = self._con.cursor()
                cur.execute(f'INSERT IGNORE INTO DIR_User SET Name=\'{user}\'')
                cur.execute(f'SELECT ID FROM DIR_User WHERE Name=\'{user}\'')
                rows = cur.fetchone()
                return rows[0]
        else:
            return -1

    def insert_user_card_list(self, user, card_list):
        id_user = self.insert_just_user(user)
        if card_list != '':
            for card in card_list.split(','):
                id_card = self.insert_just_card(card)
                if id_card !=-1 and id_user != -1:
                    with self._con:
                        cur = self._con.cursor()
                        cur.execute(f'INSERT IGNORE INTO OPT_User_Cards SET ID_User=\'{id_user}\' ID_Card=\'{id_card}\'')

    def delete_a_card_user_link(self, card):
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'DELETE IGNORE FROM OPT_User_Cards WHERE ID_Card IN (SELECT ID FROM DIR_Card WHERE CardId=\'{card}\')')

    def delete_a_card_totally(self, card):
        self.delete_a_card_user_link(card)
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'DELETE IGNORE FROM DIR_Card WHERE CardId=\'{card}\'')

    def get_all_registered_cards(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'SELECT CardId FROM DIR_Cards')
            rows = cur.fetchone()
            return [f"row[0]" for row in enumerate(rows, 1)]
    def get_all_any_cards(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'SELECT DISTINCT AnyCardId FROM REG_Event WHERE AnyCardId <> NULL AND AnyCardId <> 0')
            rows = cur.fetchone()
            return [f"row[0]" for row in enumerate(rows, 1)]

    def get_reg_events(self, time_start, time_end,  card_filter=False, controller_filter=False):
        if card_filter:
            sql_flt = ' AND AnyCardId<>NULL'
        else:
            sql_flt = ''

        if controller_filter:
            cnt_flt = ' AND Controller={}'.format(controller_filter)
        else:
            cnt_flt = ''

        with self._con:
            cur = self._con.cursor()
            cur.execute(f'SELECT TM, AnyCardId, Name from REG_Event INNER JOIN CLS_EventType ON REG_Event.EventId='
                        'CLS_EventType.ID WHERE TM >{} AND TM <{}{}{} '.format(int(time_start.timestamp()),
                        int(time_end.timestamp()),sql_flt, cnt_flt))
            return cur.fetchall()

    def insert_an_event(self, time, event_id, card, controller, flag):
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'INSERT INTO REG_Event (TM, AnyCardId,  Controller, Flag) '
                        'select({}, {}, {} ,{}, {})'.format(time.timestamp(), event_id, card, controller,flag))


