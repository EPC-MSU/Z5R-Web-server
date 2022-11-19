import sqlite3


def get_users_list():
    con = sqlite3.connect('service_data/z5r.db')
    cur = con.cursor()
    cur.execute('SELECT card, username from users')
    return dict(cur.fetchall())


def get_events_by_date(start_datetime, end_datetime, card_filter=False):
    if card_filter:
        sql_flt = ' AND card != "000000000000"'
    else:
        sql_flt = ''
    con = sqlite3.connect('service_data/z5r.db')
    cur = con.cursor()
    cur.execute(
        'SELECT time, card, event_name FROM events WHERE time > {} AND time < {}{} ORDER BY time'.format(
            int(start_datetime.timestamp()), int(end_datetime.timestamp()), sql_flt
        ))
    return cur.fetchall()


def em_marine(card_hex):
    if len(card_hex) != 12:
        return 'N/A'
    if card_hex[0:6] != '000000':
        return 'N/A'
    return '{:03},{:05}'.format(int(card_hex[6:8], base=16), int(card_hex[8:12], base=16))


def inject_top_bar(page):
    index_body = page.find('<body>')
    index_style = page.find('<style>')
    if index_body == -1 or index_style == -1 or index_body < index_style:
        return page
    injection_body = """
     <div class="topnav">
  <a href="/control">Control</a>
  <a href="/attendance">Attendance</a>
  <a href="/users">Users</a>
</div>
    """
    injection_style = """
.topnav {
  background-color: #333;
  overflow: hidden;
}

/* Style the links inside the navigation bar */
.topnav a {
  float: left;
  color: #f2f2f2;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
  font-size: 17px;
}

/* Change the color of links on hover */
.topnav a:hover {
  background-color: #ddd;
  color: black;
}
        """
    return page[:index_style+7] + injection_style + \
        page[index_style+7:index_body+6] + injection_body + page[index_body+6:]
