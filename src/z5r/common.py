import sqlite3


def get_events_by_date(databases, start_datetime, end_datetime, card_filter=False):
    if card_filter:
        sql_flt = ' AND card != "000000000000"'
    else:
        sql_flt = ''
    res_cat = list()
    for dbname in databases:
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        cur.execute(
            'SELECT time, card, event_name FROM events WHERE time > {} AND time < {}{} ORDER BY time'.format(
                int(start_datetime.timestamp()), int(end_datetime.timestamp()), sql_flt
            ))
        res = cur.fetchall()
        if len(res) == 0:
            continue
        res_cat += res

    return res_cat
