import sqlite3
from .common import em_marine, get_users_list


MAX_GET_CARDS_FORM = 2000 // 50 - 10  # GET request is limited to 2k in the worst case. Each entry = 50. And margin.


def _update_users(query):
    con = sqlite3.connect('service_data/z5r.db')
    cur = con.cursor()

    for key in query:
        if len(key) != 17:
            continue
        if key.startswith('name_'):
            cur.execute(f'INSERT OR REPLACE INTO users VALUES ("{key[5:18]}", "{query[key][0]}")')

    con.commit()
    return


def _update_controllers(query, controllers_dict):
    for key in query:
        if len(key) != 17:
            continue
        if key.startswith('name_') and query[key][0] != '':  # User with a name
            for sn in controllers_dict:
                card = key[5:18]
                if card[0:6] == '000000':
                    flags = 32
                else:
                    flags = 0
                controllers_dict[sn].add_card(card, flags, 255)


def users_handler(query, controllers_dict):
    if 'action' not in query:  # No action - no further proceeding
        return
    if query['action'][0] == 'update_users':
        _update_users(query)
    elif query['action'][0] == 'update_controllers':
        _update_controllers(query, controllers_dict)
    else:
        pass


def _get_all_cards():
    con = sqlite3.connect('service_data/z5r.db')
    cur = con.cursor()
    cur.execute('SELECT DISTINCT card from events ORDER BY time')
    res = cur.fetchall()
    cards = [x[0] for x in res if x[0] != '000000000000']  # Filter and unwrap
    return cards


def get_users_page():
    head = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <title>Z5R users page</title>
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
    <button name="action" type="submit" value="update_users" width="20%">Update users</button>
    <button name="action" type="submit" value="update_controllers" width="20%">
        Update controllers with all user keys with names
    </button>
    <table style="width: 100%;">
    <tbody>
    <tr>
    <td>
    Name
    </td>
    <td>
    Card HEX
    </td>
    <td>
    Card Em-Marine
    </td>
    <td>
    Control
    </td>
    """

    cards = _get_all_cards()
    users = get_users_list()
    lowrow = ''

    for card in cards[:MAX_GET_CARDS_FORM]:
        row = """
        <tr>
        <td>"""

        if card in users:
            name = users[card]
        else:
            name = ''

        row += f"""
        <label for="name_{card}">Name:</label>
        <input type="text" id="name_{card}" name="name_{card}" value="{name}" maxlength="30">
        </td>
        <td>
        """

        row += f"""
        {card}
        </td>
        <td>
        {em_marine(card)}
        </td>
        <td>"""

        if name != '':  # This user has a name
            row += f'<button name="delete" type="submit" value="{card}">Delete user</button>'
        row += """
        </td>
        </tr>"""
        if name != '':  # Priority for registered users with a name
            answer += row
        else:
            lowrow += row
    answer += lowrow

    # Table end
    answer += """
    </tbody>
    </table>
    </form>"""

    if len(cards) > MAX_GET_CARDS_FORM:
        answer += f"""
        <p style="color: red; font-size: x-large;">Card number limit {MAX_GET_CARDS_FORM} reached. Rewrite code.</p>
        """

    answer += tail
    return answer
