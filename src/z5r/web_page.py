import logging

def per_controller_page(sn):
    logging.debug(f'Invoked per_controller_page with sn={sn}')
    # Heading
    answer = '<h2 style="text-align: center;">Controller SN{}</h1>'.format(sn)

    # Forms outside the table
    forms = ['open_door', 'set_mode', 'set_door_params', 'add_cards', 'del_cards', 'clear_cards']
    for form in forms:
        answer += """
<form action="/" id="{}_{}" method="get">
<input type="hidden" name="sn" value="{}">
</form>""".format(form, sn, sn)

    # Table start
    answer += """
<table style="border-collapse: collapse; width: 100%; height: 108px;" border="1">
<tbody>"""

    answer += f"""
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;">
<button name="action" type="submit" value="{forms[0]}" form="{forms[0]}_{sn}">Open door</button>
</td>
<td style="width: 33.3333%; height: 18px;">
<label for="{forms[0]}_direction">Direction:</label>
<input type="text" name="{forms[0]}_direction" value="0" form="{forms[0]}_{sn}">
</td>
<td style="width: 33.3333%; height: 18px;">
Opens the door. Direction 0 is for entrance. Direction 1 is for exit.
</td>
</tr>"""

    answer += f"""
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;">
<button name="action" type="submit" value="{forms[1]}" form="{forms[1]}_{sn}">Set mode</button>
</td>
<td style="width: 33.3333%; height: 18px;">
<label for="{forms[1]}_mode">Mode:</label>
<input type="text" name="{forms[1]}_mode" value="0" form="{forms[1]}_{sn}">
</td>
<td style="width: 33.3333%; height: 18px;">
Sets controller mode: 0 - normal, 1 - block, 2 - free passage, 3 - waiting for free passage.
</td>
</tr>"""

    answer += f"""
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;">
<button name="action" type="submit" value="{forms[2]}" form="{forms[2]}_{sn}">Set door params</button>
</td>
<td style="width: 33.3333%; height: 18px;">
<label for="{forms[2]}_open">Open:</label>
<input type="text" name="{forms[2]}_open" value="30" form="{forms[2]}_{sn}"><br>
<label for="{forms[2]}_open_control">Open control:</label>
<input type="text" name="{forms[2]}_open_control" value="50" form="{forms[2]}_{sn}"><br>
<label for="{forms[2]}_close_control">Close control:</label>
<input type="text" name="{forms[2]}_close_control" value="50" form="{forms[2]}_{sn}">
</td>
<td style="width: 33.3333%; height: 18px;">
Sets the time for opening and closing of the door. Open is time for opening door signal [1/10s].
Open control is time of control for opened door [1/10s]). Close control is time of control for closing door [1/10s].
</td>
</tr>"""

    answer += f"""
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;">
<button name="action" type="submit" value="{forms[3]}" form="{forms[3]}_{sn}">Add cards</button>
</td>
<td style="width: 33.3333%; height: 18px;">
<label for="{forms[3]}_card">Card number in HEX:</label>
<input type="text" name="{forms[3]}_card" value="123456789ABC" form="{forms[3]}_{sn}"><br>
<label for="{forms[3]}_flags">Flags:</label>
<input type="text" name="{forms[3]}_flags" value="0" form="{forms[3]}_{sn}"><br>
<label for="{forms[3]}_tz">Time zone:</label>
<input type="text" name="{forms[3]}_tz" value="255" form="{forms[3]}_{sn}">
</td>
<td style="width: 33.3333%; height: 18px;">
Insert manual here
</td>
</tr>"""

    answer += f"""
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;">
<button name="action" type="submit" value="{forms[4]}" form="{forms[4]}_{sn}">Delete cards</button>
</td>
<td style="width: 33.3333%; height: 18px;">
<label for="{forms[4]}_card">Card number in HEX:</label>
<input type="text" name="{forms[4]}_card" value="123456789ABC" form="{forms[4]}_{sn}">
</td>
<td style="width: 33.3333%; height: 18px;">
Insert manual here
</td>
</tr>"""

    answer += f"""
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;">
<button name="action" type="submit" value="{forms[5]}" form="{forms[5]}_{sn}">Clear cards</button>
</td>
<td style="width: 33.3333%; height: 18px;">
</td>
<td style="width: 33.3333%; height: 18px;">
Insert manual here
</td>
</tr>"""

    # Table end
    answer += """
</tbody>
</table>
"""
    return answer


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
    for sn in controllers_dict:
        answer += per_controller_page(sn)
    answer += per_controller_page(0)
    answer += tail
    return answer
