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

    # Prepare data
    users = get_users_list()
    cards = _get_all_cards()
    processed_cards = list()
    cards_count = 0

    # First section is known users
    for card in users:
        answer +=  f"""
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
