import sqlite3
import re
import logging
from .dbz5r import  DbZ5R


def get_users_list():
    #con = sqlite3.connect('service_data/z5r.db')
    #cur = con.cursor()
    #cur.execute('SELECT card, username from users')
    #return dict(cur.fetchall())
    dbcon = DbZ5R()
    return dbcon.get_users_cards()


def get_events_by_date(start_datetime, end_datetime, card_filter=False, controller_filter=False):
    if card_filter:
        sql_flt = ' AND card <> NULL'
    else:
        sql_flt = ''

    if controller_filter:
        cnt_flt = ' AND controller == {}'.format(controller_filter)
    else:
        cnt_flt = ''

    #con = sqlite3.connect('service_data/z5r.db')
    #cur = con.cursor()
    #cur.execute(
    #    'SELECT time, card, event_name FROM events WHERE time > {} AND time < {}{}{} ORDER BY time'.format(
    #        int(start_datetime.timestamp()), int(end_datetime.timestamp()), sql_flt, cnt_flt)
    #)
    #res = cur.fetchall()

    dbcon = DbZ5R()
    res = dbcon.get_reg_events(start_datetime, end_datetime, card_filter, controller_filter)

    logging.debug(f'SQL query for date range ({start_datetime} - {end_datetime}. Card filter {card_filter}. '
                  f'Controller filter {controller_filter}. Produced {len(res)} results.')
    return res


def em_marine(card_hex):
    if len(card_hex) != 12:
        return 'N/A'
    if card_hex[0:6] != '000000':
        return 'N/A'
    return '{:03},{:05}'.format(int(card_hex[6:8], base=16), int(card_hex[8:12], base=16))


def em_marine2hex(em_marine):
    high_byte = int(em_marine[0:3])
    low_bytes = int(em_marine[4:9])
    return '000000{:02X}{:04X}'.format(high_byte, low_bytes)


def validate_em_marine(code_string):
    if re.fullmatch('[0-9]{3},[0-9]{5}', code_string) is not None:
        return True
    else:
        return False


def validate_hex(code_string):
    if re.fullmatch('[0-9a-fA-F]{12}', code_string) is not None:
        return True
    else:
        return False


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
