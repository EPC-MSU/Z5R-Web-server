import sqlite3
from .common import em_marine


def users_handler(query, controllers_dict):
    pass


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

    for card in cards:
        answer += f"""
    <tr>
    <td>
    {card}
    </td>
    <td>
    {em_marine(card)}
    </td>
    <td>
    <label for="ttt_open">Open:</label>
    <input type="text" id="ttt_open" name="ttt_open" value="30"><br>
    <label for="ttt_open_control">Open control:</label>
    <input type="text" id="ttt_open_control" name="ttt_open_control" value="50">
    <br>
    <label for="ttt_close_control">Close control:</label>
    <input type="text" id="ttt_close_control" name="ttt_close_control" value="50">
    </td>
    </tr>"""

    # Table end
    answer += """
    </tbody>
    </table>
    </form>"""

    answer += tail
    return answer
