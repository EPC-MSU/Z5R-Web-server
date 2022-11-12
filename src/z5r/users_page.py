import sqlite3
from .common import em_marine


def users_handler(query, controllers_dict):
    return query, controllers_dict


def get_users_page(controllers_dict):
    head = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <title>Z5R control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta charset="UTF-8">
    <style>

    table, th, td {
      border: 1px solid black;
      border-collapse: collapse;
    }

    div {
      padding: 5px;
    }
    </style>
    </head>
    <body>
    <h1 style="text-align: center;">Z5R-Web users page</h1>
    """
    tail = """
    </body>
    </html>
    """
    answer = head

    # Table start
    answer += """
    <form action="/users" id="users_form" method="get">
    <button name="action" type="submit" value="update_users">Update users</button>
    <table style="width: 100%; height: 108px;">
    <tbody>
    <tr>
    <td>
    Card HEX
    </td>
    <td>
    Card Em-Marine
    </td>
    <td>
    Name
    </td>
    """

    # Load all cards from databases
    databases = ['service_data/{}_events.db'.format(sn) for sn in controllers_dict]
    cards = list()
    for dbname in databases:
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        cur.execute('SELECT DISTINCT card from events ORDER BY time')
        res = cur.fetchall()
        if len(res) == 0:
            continue
        cards += res
    # Filter duplicates
    seen = set()
    cards = [x for x in cards if not (x in seen or seen.add(x))]

    for card in cards:
        answer += f"""
        <tr>
        <td>
        {card[0]}
        </td>
        <td>
        {em_marine(card[0])}
        </td>
        <td>"""

        answer += f"""
        <label for="name_{card[0]}">Name:</label>
        <input type="text" id="name_{card[0]}" name="name_{card[0]}" value="">"""

        answer += """</td>
        </tr>"""

    # Table end
    answer += """
    </tbody>
    </table>
    </form>"""

    answer += tail
    return answer
