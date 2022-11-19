import sqlite3
from .common import em_marine, get_users_list, validate_em_marine, em_marine2hex


MAX_GET_CARDS_FORM = 2000 // 50 - 10  # GET request is limited to 2k in the worst case. Each entry = 50. And margin.


def _update_users(query):
    con = sqlite3.connect('service_data/z5r.db')
    cur = con.cursor()

    for key in query:
        if len(key) != 17 or query[key][0] == '':  # Do not add users with empty names or invalid key length
            continue
        if key.startswith('name_'):
            cur.execute(f'INSERT OR REPLACE INTO users VALUES ("{key[5:18]}", "{query[key][0]}")')

    con.commit()


def _add_one_user(name, card, em_marine, method):
    if method == 'HEX':
        card_key = card
    elif method == 'em_marine':
        card_key = em_marine2hex(em_marine)
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
    elif 'add_one' in query:
        method = None
        if query['add_one'][0] != '':  # Button have no value
            return
        if query['name_manual'][0] == '':  # Name must not be empty for new users
            return
        if len(query['card_manual'][0]) == 12:  # Validate card number via length (lousy way)
            method = 'HEX'
        elif validate_em_marine(query['em_marine_manual'][0]):  # Validate em_marine
            method = 'em_marine'
        else:
            return
        _add_one_user(query['name_manual'][0], query['card_manual'][0], query['em_marine_manual'][0], method)


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
    <form action="/users" id="users_form" method="get">
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
        <td>
        <label for="card_manual">Card HEX:</label>
        <input type="text" id="card_manual" name="card_manual" value="" maxlength="12">
        </td>
        <td>
        <label for="em_marine_manual">Em-Marine:</label>
        <input type="text" id="em_marine_manual" name="em_marine_manual" value="" maxlength="9">
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
    cards_count = 0

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
        <button name="delete" type="submit" value="{card}">Delete user</button>
        </td>
        </tr>"""
        processed_cards.append(card)

        cards_count += 1
        if cards_count >= MAX_GET_CARDS_FORM:
            break

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

        cards_count += 1
        if cards_count >= MAX_GET_CARDS_FORM:
            break

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

    if cards_count >= MAX_GET_CARDS_FORM:
        answer += f"""
        <p style="color: red; font-size: x-large;">Card number limit {MAX_GET_CARDS_FORM} reached. Rewrite code.</p>
        """

    answer += tail
    return answer
