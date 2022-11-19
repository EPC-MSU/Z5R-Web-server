import sqlite3
from .common import em_marine, get_users_list, validate_em_marine, em_marine2hex, validate_hex


def _update_users(query):
    con = sqlite3.connect('service_data/z5r.db')
    cur = con.cursor()

    for key in query:
        if len(key) != 17 or query[key][0] == '':  # Do not add users with empty names or invalid key length
            continue
        if key.startswith('name_'):
            cur.execute(f'INSERT OR REPLACE INTO users VALUES ("{key[5:18]}", "{query[key][0]}")')

    con.commit()


def _add_one_user(name, card, method):
    if method == 'HEX':
        card_key = card
    elif method == 'em_marine':
        card_key = em_marine2hex(card)
    else:  # Only support 2 methods
        return
    con = sqlite3.connect('service_data/z5r.db')
    cur = con.cursor()
    cur.execute(f'INSERT OR REPLACE INTO users VALUES ("{card_key}", "{name}")')
    con.commit()


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
    if 'action' in query:  # Processing global actions
        if query['action'][0] == 'update_users':
            _update_users(query)
        elif query['action'][0] == 'update_controllers':
            _update_controllers(query, controllers_dict)
        else:
            pass

    elif 'delete' in query:
        con = sqlite3.connect('service_data/z5r.db')
        cur = con.cursor()
        card = query['delete'][0]
        if len(card) != 12:
            return
        cur.execute(f'DELETE FROM users WHERE card == "{card}"')
        con.commit()
        for sn in controllers_dict:
            controllers_dict[sn].del_card(card)

    elif 'add_one' in query:
        method = None
        if query['add_one'][0] != '':  # Button have no value
            return
        if query['name_manual'][0] == '':  # Name must not be empty for new users
            return
        if validate_hex(query['card_manual'][0]):  # Validate card number as HEX
            method = 'HEX'
        elif validate_em_marine(query['card_manual'][0]):  # Validate as em_marine
            method = 'em_marine'
        else:
            return
        _add_one_user(query['name_manual'][0], query['card_manual'][0], method)


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
      text-align: center
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
    <form action="/users" id="users_form" method="post">
    <button name="action" type="submit" value="update_users">Update users</button>
    <button name="action" type="submit" value="update_controllers">
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

    # Manual add user
    answer += """
        <tr>
        <td>
        <label for="name_manual">Name:</label>
        <input type="text" id="name_manual" name="name_manual" value="" maxlength="30">
        </td>
        <td colspan="2">
        <label for="card_manual">Card HEX or Em-Marine:</label>
        <input type="text" id="card_manual" name="card_manual" value="" maxlength="12">
        </td>
        <td>
        <button name="add_one" type="submit" value="">Add user</button>
        </td>
        </tr>"""

    # Insert separator
    answer += """
            <tr>
            <td colspan="4" style="background-color:lightgray">
            Registered users
            </td>
            </tr>"""

    # Prepare data
    users = get_users_list()
    cards = _get_all_cards()
    processed_cards = list()

    # First section is known users
    for card in users:
        answer += f"""
        <tr>
        <td>
        <label for="name_{card}">Name:</label>
        <input type="text" id="name_{card}" name="name_{card}" value="{users[card]}" maxlength="30">
        </td>
        <td>
        {card}
        </td>
        <td>
        {em_marine(card)}
        </td>
        <td>
        <button name="delete" type="submit" value="{card}">Delete & block user</button>
        </td>
        </tr>"""
        processed_cards.append(card)

    # Insert separator
    answer += """
        <tr>
        <td colspan="4" style="background-color:lightgray">
        Unknown cards
        </td>
        </tr>"""

    # Then go unknown cards
    for card in cards:
        if card in processed_cards:  # We do not process the cards that were processed in first section
            continue

        answer += f"""
        <tr>
        <td>
        <label for="name_{card}">Name:</label>
        <input type="text" id="name_{card}" name="name_{card}" value="" maxlength="30">
        </td>
        <td>
        {card}
        </td>
        <td>
        {em_marine(card)}
        </td>
        <td>
        </td>
        </tr>"""

    # Table end
    answer += """
    </tbody>
    </table>
    </form>"""

    answer += tail
    return answer
