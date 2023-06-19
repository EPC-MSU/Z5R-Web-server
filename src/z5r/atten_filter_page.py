import sqlite3
from .dbz5r import DbZ5R

import sqlite3
from .common import em_marine, validate_em_marine, em_marine2hex, validate_hex
from .dbz5r import DbZ5R


def _attendance_filter_handler(query):
    if 'search' in query:
        name = query['name_select'][0]
        dt_start = query['dt_start'][0]
        dt_end = query['dt_end'][0]
        return [name, dt_start, dt_end]
    return list()


def get_attendance_filter_page(query):
    head = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <title>Z5R attendance filter page</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta charset="UTF-8">
    <style>

    table, th, td {
      border: 1px solid black;
      border-collapse: collapse;
      text-align: center
    }

    div {
      padding: 5px;
    }
    </style>
    </head>
    """
    dbcon = DbZ5R()
    names = dbcon.get_user_names()
    name_s = ''
    dt1 = ''
    dt2 = ''
    if len(names) > 0:
        name_s = names[0]
        dt1 = names[1]
        dt2 = names[2]

    # Prepare data
    user_att = _attendance_filter_handler(query)

    head += f"""
    <body>
    <h1 style="text-align: center;">Z5R Attendance | Filter page</h1>
    <form action="/attendance_filter" id="atten_filter_form" method="post">
    <label for="name_manual">Name:</label>
        <select name="name_select" value="{name_s}" size="1">
        <option selected></option>
    """
    for name in names:
        head += f"""<option>{name}</option>"""

    head += f"""
        </select>
    <label for="dt_start">Start Date:</label>
        <input type="date" id="dt_start" name="dt_start" value="{dt1}" maxlength="30">
    <label for="dt_start">End Date:</label>
        <input type="date" id="dt_start" name="dt_end" value="{dt2}" maxlength="30">
    <button name="search" type="submit" value="search">
        Search
    </button>
    <h2  style="text-align: center;">Results</h2>

    """
    tail = """
    </form>
    </body>
    </html>
    """
    answer = head

    # Table start
    answer += """
    """

    user_spy_data = list()
    if len (user_att) > 0 and user_att[0] != '' and user_att[1] !='' and user_att[2] != '':
        dbcon = DbZ5R()
        user_spy_data = dbcon.get_user_time(user_att[0], user_att[1], user_att[2])

    if len(user_att) != 0:
        answer += """
        <table style="width: 100%;">
        <tbody>
        <tr>
        <th>
        Date
        </th>
        <th>
        First Time
        </th>
        <th>
        Last Time
        </th>
        """
        if len(user_spy_data) > 0:
            for item in user_spy_data:
                answer += f"""
                <tr>
                <td>
                {item[0]}
                </td>
                <td>
                {item[1]}
                </td>
                <td>
                {item[2]}
                </td>
                </tr>"""

    # Table end
        answer += """
        </tbody>
        </table>
        </form>"""

    answer += tail
    return answer
