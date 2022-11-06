def per_controller_page(sn):
    answer = '<h2 style="text-align: center;">Controller SN{}</h1>'.format(sn)
    forms = ['open_door', 'set_mode', 'set_door_params', 'add_cards', 'del_cards', 'clear_cards']
    for form in forms:
        answer += """
<form action="/" id="{}" method="get">
<input type="hidden" name="sn" value="{}">
</form>""".format(form, sn)
    return answer + """
<table style="border-collapse: collapse; width: 100%; height: 108px;" border="1">
<tbody>
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;"><button name="action" type="submit" value="open_door" form="open_door">Open door</button></td>
<td style="width: 33.3333%; height: 18px;"><label for="open_door_direction">Direction:</label><input type="text" id="open_door_direction" name="open_door_direction" value="0" form="open_door"></td>
<td style="width: 33.3333%; height: 18px;">Opens the door. Direction 0 is for entrance. Direction 1 is for exit.</td>
</tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;"><button name="action" type="submit" value="set_mode" form="set_mode">Set mode</button></td>
<td style="width: 33.3333%; height: 18px;"><label for="set_mode_mode">Mode:</label><input type="text" id="set_mode_mode" name="set_mode_mode" value="0" form="set_mode"></td>
<td style="width: 33.3333%; height: 18px;">Sets controller mode: 0 - normal, 1 - block, 2 - free passage, 3 - waiting for free passage.</td>
</tr>
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;"><button name="action" type="submit" value="set_door_params" form="set_door_params">Set door params</button></td>
<td style="width: 33.3333%; height: 18px;"><label for="set_door_params_open">Open:</label><input type="text" id="set_door_params_open" name="set_door_params_open" value="30" form="set_door_params"><br>
<label for="set_door_params_open_control">Open control:</label><input type="text" id="set_door_params_open_control" name="set_door_params_open_control" value="50" form="set_door_params"><br>
<label for="set_door_params_close_control">Close control:</label><input type="text" id="set_door_params_close_control" name="set_door_params_close_control" value="50" form="set_door_params"></td>
<td style="width: 33.3333%; height: 18px;">Sets the time for opening and closing of the door. Open is time for opening door signal [1/10s]. Open control is time of control for opened door [1/10s]). close_control - is time of control for closing door [1/10s].</td>
</tr>
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;"><button name="action" type="submit" value="add_cards" form="add_cards">Add cards</button></td>
<td style="width: 33.3333%; height: 18px;"><label for="add_cards_card">Card number in HEX:</label><input type="text" id="add_cards_card" name="add_cards_card" value="123456789ABC" form="add_cards"><br>
<label for="add_cards_flags">Flags:</label><input type="text" id="add_cards_flags" name="add_cards_flags" value="0" form="add_cards"><br>
<label for="add_cards_tz">Time zone:</label><input type="text" id="add_cards_tz" name="add_cards_tz" value="255" form="add_cards"></td>
<td style="width: 33.3333%; height: 18px;">Some help</td>
</tr>
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;"><button name="action" type="submit" value="del_cards" form="del_cards">Delete cards</button></td>
<td style="width: 33.3333%; height: 18px;"><label for="del_cards_card">Card number in HEX:</label><input type="text" id="del_cards_card" name="del_cards_card" value="123456789ABC" form="del_cards"></td>
<td style="width: 33.3333%; height: 18px;">Some help</td>
</tr>
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;"><button name="action" type="submit" value="clear_cards" form="clear_cards">Clear cards</button></td>
<td style="width: 33.3333%; height: 18px;"></td>
<td style="width: 33.3333%; height: 18px;">Some help</td>
</tr>
</tbody>
</table>
"""

def get_page(controllers_dict):
    head = """
<html>
<head>
</head>
<body>
<h1 style="text-align: center;">Z5R-Web server control</h1>
"""
    tail = """
</body>
</html>
"""
    answer = head
    for controller in controllers_dict:
        answer += per_controller_page(controller.sn)
    answer += per_controller_page(0)
    answer += tail
    return answer
