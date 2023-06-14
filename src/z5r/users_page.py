import sqlite3
from .common import em_marine, get_user_cards_list, validate_em_marine, em_marine2hex, validate_hex
from .dbz5r import DbZ5R

def _add_one_user(name, cards, controllers_dict):
    int_cards = list()
    for card in cards.split(';'):
        method = None
        if validate_hex(card):  # Validate card number as HEX
            method = 'HEX'
        elif validate_em_marine(card):  # Validate as em_marine
            method = 'em_marine'
        else:
            continue
        if method == 'HEX':
            card_key = card
        elif method == 'em_marine':
            card_key = em_marine2hex(card)
        else:  # Only support 2 methods
            continue
        int_card = int(card_key, 16)
        int_cards.append(int_card)
        for sn in controllers_dict:
            card_hex_str = '{:012X}'. format(int_card)
            if card_hex_str[0:6] == '000000':
                flags = 32
            else:
                flags = 0
            controllers_dict[sn].add_card(card_hex_str, flags, 255)
    dbcon = DbZ5R()
    dbcon.insert_user_card_list(name, int_cards)


def _delete_data(name, card0, controllers_dict):
    dbcon = DbZ5R()
    card_list = list()

    if name != '':
        card_list = dbcon.get_user_cards(name)
    elif card0 != '':
        card_list.append(card0)

    dbcon.delete_data(name, card0)
    for card in card_list:
        for sn in controllers_dict:
            controllers_dict[sn].del_card(card)


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
        if query['action'][0] == 'update_controllers':
            _update_controllers(query, controllers_dict)
        else:
            pass

    elif 'delete' in query:
        name_card = query['delete'][0]
        elist = name_card.split('_')
        name = ''
        card0 = ''
        for i, key in enumerate(elist):
            if key == 'name':
                name = elist[i+1]
            elif key == 'card':
                card0 = elist[i+1]

        _delete_data(name, card0, controllers_dict)
    elif 'add_one' in query:
        if query['add_one'][0] != '':  # Button have no value
            return
        _add_one_user(query['name_manual'][0], query['card_manual'][0], controllers_dict)


def _get_all_cards_10_min():
    dbcon = DbZ5R()
    return dbcon.get_all_any_cards_last_10_min()


def _get_free_registered_cards():
    dbcon = DbZ5R()
    return dbcon.get_cards_registered_free()


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
    <button name="action" type="submit" value="update_controllers">
        Force inserting all the registered cards into the controller's DBs
    </button>
    <table style="width: 100%;">
    <tbody>
    <tr>
    <td>
    Name
    </td>
    <td>
    Cards HEX
    </td>
    <td>
    Cards Em-Marine
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
        <label for="card_manual">Cards HEX or Em-Marine:</label>
        <input type="text" id="card_manual" name="card_manual" value="" maxlength="48">
        </td>
        <td>
        <button name="add_one" type="submit" value="">Add data</button>
        </td>
        </tr>"""

    # Insert separator
    answer += """
            <tr>
            <td colspan="4" style="background-color:lightgray">
            Registered users and cards
            </td>
            </tr>"""

    # Prepare data
    users = get_user_cards_list()
    cards = _get_all_cards_10_min()
    processed_cards = list()
    free_cards = _get_free_registered_cards()

    # First section is known users
    for item in users:
        card0 = ''
        em_marine_cards = ''
        hex_cards = ''
        name = item[0]
        cards = item[1]
        if name is not None:
            card0 += 'name_' + name + '_'
        if cards != 'None':
            card0 += 'card_' + cards.split(';')[0]
            for card in cards.split(';'):
                if card is not None:
                    hex_card = '{:012X}'.format(int(card))
                    processed_cards.append(card)
                    em_marine_cards += em_marine(hex_card) + '; '
                    hex_cards += hex_card + '; '

            hex_cards = hex_cards[:-2]
            em_marine_cards = em_marine_cards[:-2]

        answer += f"""
        <tr>
        <td>
        {name}
        </td>
        <td>
        {hex_cards}
        </td>
        <td>
        {em_marine_cards}
        </td>
        <td>
        <button name="delete" type="submit" value="{card0}">Delete user & block cards</button>
        </td>
        </tr>"""

    for free_card in free_cards:
        free_hex_card = '{:012X}'.format(int(free_card))
        free_em_marine=em_marine(free_hex_card)
        free_card0 = 'card_' + free_card
        answer += f"""
                <tr>
                <td>
                </td>
                <td>
                {free_hex_card}
                </td>
                <td>
                {free_em_marine}
                </td>
                <td>
                <button name="delete" type="submit" value="{free_card0}">Block card</button>
                </td>
                </tr>"""

    # Insert separator
    answer += """
        <tr>
        <td colspan="4" style="background-color:lightgray">
        Unregistered card events (last 10 minutes)
        </td>
        </tr>"""

    # Then go unknown cards
    if cards != 'None':
        for card in cards:
            if card in processed_cards:  # We do not process the cards that were processed in first section
                continue

            answer += f"""
            <tr>
            <td>
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


