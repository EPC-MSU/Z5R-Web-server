import pymysql
class DbZ5R:
    def __init__(self, login='z5r', password='Ahthohj0ooJa'):
        self._login = login
        self._password = password
        self._con = self.db_connect()

    def db_connect(self):
        return pymysql.connect('localhost', self._login, self._password, 'z5r')

    def get_user_names(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute("SELECT Name from DIR_User order by Name")
            rows = cur.fetchall()
            return [f"row[0]" for row in enumerate(rows, 1)]

    def get_users_cards(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute("SELECT Name, GROUP_CONCAT(CardId, SEPARATOR ',') FROM DIR_Card "
                        "LEFT JOIN  OPT_User_Cards ON DIR_Card.ID = "
                        "OPT_User_Cards.ID_Card RIGHT JOIN DIR_User ON DIR_User.ID = OPT_User_Cards.ID_USER"
                        "GROUP BY NAME "
                        "ORDER BY Name")
            rows = cur.fetchall()
            return [[f"row[0]", f"[row[1]"] for row in enumerate(rows, 1)]

    def insert_just_card(self, card):
        if card != '':
            with self._con:
                cur = self._con.cursor()
                cur.execute(f'INSERT IGNORE INTO DIR_Card SET CardId=\'{card}\'')
                cur.execute(f'SELECT ID FROM DIR_Card WHERE CardId=\'{card}\'')
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
                id_card = self.insert_just_card()
                if id_card !=-1 and id_user != -1:
                    with self._con:
                        cur = self._con.cursor()
                        cur.execute(f'INSERT IGNORE INTO OPT_User_Cards SET UserId=\'{id_user}\' CardId=\'{id_card}\'')

    def delete_a_card(self, card):
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'DELETE IGNORE INTO OPT_User_Cards WHERE CadrId=\'{card}\'')
    def get_all_cards(self):
        with self._con:
            cur = self._con.cursor()
            cur.execute(f'SELECT CardId FROM DIR_Cards')
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


