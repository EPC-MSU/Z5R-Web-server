import pymysql
class DbZ5R:
    def __init__(self, login, password):
        self._login = login
        self._password = password
    def db_connect(self):
        return  pymysql.connect('localhost', self._login, self._password, 'Z5r')

    def get_user_names(self):
        con = self.db_connect()
        with con:
            cur = con.cursor()
            cur.execute("SELECT Name from DIR_User order by Name")
            rows = cur.fetchall()
            return [f"row[0]" for row in enumerate(rows, 1)]

    def get_users_cards(self):
        con = self.db_connect()
        with con:
            cur = con.cursor()
            cur.execute("SELECT Name, IdCard FROM DIR_Card LEFT JOIN  OPT_User_Cards ON DIR_Card.ID = "
                        "OPT_User_Cards.ID_Card RIGHT JOIN DIR_User ON DIR_User.ID = OPT_User_Cards.ID_USER"
                        "ORDER BY Name")
            rows = cur.fetchall();
            return [[f"row[0]", f"[row[1]"] for row in enumerate(rows, 1)]

    def insert_just_card(self, card):
        if card != '':
            con = self.db_connect()
            with con:
                cur = con.cursor()
                cur.execute(f'INSERT IGNORE INTO DIR_Card SET CardId=\'{card}\'')
                cur.execute(f'SELECT ID FROM DIR_Card WHERE Name=\'{card}\'')
                rows = cur.fetchall()
                return rows[0]
        else:
            return -1

    def insert_just_user(self, user):
        if user != '':
            con = self.db_connect()
            with con:
                cur = con.cursor()
                cur.execute(f'INSERT IGNORE INTO DIR_User SET Name=\'{user}\'')
                cur.execute(f'SELECT ID FROM DIR_User WHERE Name=\'{user}\'')
                rows = cur.fetchone()
                return rows[0]
        else:
            return -1

    def insert_user_card_list(self, user, card_list):
        con = self.db_connect()
        id_user = self.insert_just_user(user)
        con = self.db_connect()
        if card_list != '':
            for card in card_list.split(','):
                id_card = self.insert_just_card()
                if id_card !=-1 and id_user != -1:
                    with con:
                        cur = con.cursor()
                        cur.execute(f'INSERT IGNORE INTO OPT_User_Cards SET UserId=\'{id_user}\' CardId=\'{id_card}\'')

