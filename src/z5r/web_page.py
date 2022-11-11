import logging
import sqlite3
from datetime import datetime
from datetime import timedelta


def action_handler(query, controllers_dict):
    try:
        _ = controllers_dict[int(query['sn'][0])]
    except ValueError:
        logging.error('Could not resolve a designated controller from query.')
        return
    except KeyError:  # There is no action
        return
    except TypeError as e:
        logging.error(e)
        return
    if query['action'][0] == 'open_door':
        try:
            cnt = controllers_dict[int(query['sn'][0])]
        except KeyError as e:
            logging.error('Serial number not found. {}'.format(e))
            return
        cnt.open_door(int(query['open_door_direction'][0]))
    elif query['action'][0] == 'set_mode':
        pass
    elif query['action'][0] == 'set_door_params':
        pass
    elif query['action'][0] == 'add_cards':
        pass
    elif query['action'][0] == 'del_cards':
        pass
    elif query['action'][0] == 'clear_cards':
        pass
    else:
        logging.error('Unknown action.')


def get_attendance_page(controllers_dict):
    head = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <title>Z5R attendance</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta charset="UTF-8">
    <style>
    .collapsible {
      background-color: #777;
      color: white;
      cursor: pointer;
      padding: 5px;
      width: 100%;
      border: 2px solid #888;
      text-align: left;
      outline: none;
      font-size: 15px;
    }

    .active, .collapsible:hover {
      background-color: #555;
    }

    .content {
      padding: 0 5px;
      display: none;
      overflow: hidden;
      background-color: #f1f1f1;
    }

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
    <h1 style="text-align: center;">Z5R-Web general attendance</h1>
    """
    tail = """

    <script>
    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
      coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
          content.style.display = "none";
        } else {
          content.style.display = "block";
        }
      });
    }
    </script>

    </body>
    </html>
    """
    answer = head

    # Start event collapsible view
    DAY_TO_SHOW = 5
    start = datetime.now().date() - timedelta(DAY_TO_SHOW)  # The end of this day
    days = [datetime(start.year, start.month, start.day) + timedelta(i) for i in range(0, DAY_TO_SHOW + 2)]
    databases = ['service_data/{}_events.db'.format(sn) for sn in controllers_dict]
    for day in range(0, DAY_TO_SHOW + 1):
        res = _get_events_by_date(databases, days[day], days[day + 1], card_filter=True)
        if len(res) == 0:
            continue

        def split_first_last(events_list):
            card_events = dict()
            for event in events_list:  # event is [time, card, event_name]
                if event[1] not in card_events:  # New card in list
                    card_events[event[1]] = [event[0], event[0]]  # Write it as start and end
                else:
                    if event[0] < card_events[event[1]][0]:  # If time of event is earlier than start
                        card_events[event[1]][0] = event[0]  # Write it as start time
                    if event[0] > card_events[event[1]][1]:  # If time of event is later than end
                        card_events[event[1]][1] = event[0]  # Write it as end time
            return card_events

        work_periods = split_first_last(res)
        answer += '<button type="button" class="collapsible">{}</button>'.format(days[day].strftime('%d %b'))
        answer += '<table class="content">'
        answer += '<tr><td>Card</td><td>First event</td><td>Last event</td></tr>'
        for card in work_periods:
            answer += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                card,
                datetime.fromtimestamp(int(work_periods[card][0])).strftime('%H:%M:%S'),
                datetime.fromtimestamp(int(work_periods[card][1])).strftime('%H:%M:%S')
            )
        answer += '</table>'

    answer += tail
    return answer


def _get_events_by_date(databases, start_datetime, end_datetime, card_filter=False):
    if card_filter:
        sql_flt = ' AND card != "000000000000"'
    else:
        sql_flt = ''
    res_cat = list()
    for dbname in databases:
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        cur.execute(
            'SELECT time, card, event_name FROM events WHERE time > {} AND time < {}{} ORDER BY time'.format(
                int(start_datetime.timestamp()), int(end_datetime.timestamp()), sql_flt
            ))
        res = cur.fetchall()
        if len(res) == 0:
            continue
        res_cat += res

    return res_cat


def _per_controller_page(sn):
    # Heading
    answer = '<h2 style="text-align: center;">Controller SN{}</h2>'.format(sn)

    # Forms outside the table
    forms = ['open_door', 'set_mode', 'set_door_params', 'add_cards', 'del_cards', 'clear_cards']
    for form in forms:
        answer += """
<form action="/" id="{}_{}" method="get">
<input type="hidden" name="sn" value="{}">
</form>""".format(form, sn, sn)

    # Table start
    answer += """
<table style="width: 100%; height: 108px;">
<tbody>"""

    answer += f"""
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;">
<button name="action" type="submit" value="{forms[0]}" form="{forms[0]}_{sn}">Open door</button>
</td>
<td style="width: 33.3333%; height: 18px;">
<label for="{forms[0]}_direction_{sn}">Direction:</label>
<input type="text" id="{forms[0]}_direction_{sn}" name="{forms[0]}_direction" value="0" form="{forms[0]}_{sn}">
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
<label for="{forms[1]}_mode_{sn}">Mode:</label>
<input type="text" id="{forms[1]}_mode_{sn}" name="{forms[1]}_mode" value="0" form="{forms[1]}_{sn}">
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
<label for="{forms[2]}_open_{sn}">Open:</label>
<input type="text" id="{forms[2]}_open_{sn}" name="{forms[2]}_open" value="30" form="{forms[2]}_{sn}"><br>
<label for="{forms[2]}_open_control_{sn}">Open control:</label>
<input type="text" id="{forms[2]}_open_control_{sn}" name="{forms[2]}_open_control" value="50" form="{forms[2]}_{sn}">
<br>
<label for="{forms[2]}_close_control_{sn}">Close control:</label>
<input type="text" id="{forms[2]}_close_control_{sn}" name="{forms[2]}_close_control" value="50" form="{forms[2]}_{sn}">
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
<label for="{forms[3]}_card_{sn}">Card number in HEX:</label>
<input type="text" id="{forms[3]}_card_{sn}" name="{forms[3]}_card" value="123456789ABC" form="{forms[3]}_{sn}"><br>
<label for="{forms[3]}_flags_{sn}">Flags:</label>
<input type="text" id="{forms[3]}_flags_{sn}" name="{forms[3]}_flags" value="0" form="{forms[3]}_{sn}"><br>
<label for="{forms[3]}_tz_{sn}">Time zone:</label>
<input type="text" id="{forms[3]}_tz_{sn}" name="{forms[3]}_tz" value="255" form="{forms[3]}_{sn}">
</td>
<td style="width: 33.3333%; height: 18px;">
Add cards into a controller memory. Already stored cards are overwritten with new flags and tz parameters.
Card number must be in HEX and contain 12 symbols (6 bytes).
Flags can be 8 for blocking card and 32 for cards with short code (3 bytes).
Time zone - time zone for the card.
</td>
</tr>"""

    answer += f"""
<tr style="height: 18px;">
<td style="width: 33.3333%; height: 18px;">
<button name="action" type="submit" value="{forms[4]}" form="{forms[4]}_{sn}">Delete cards</button>
</td>
<td style="width: 33.3333%; height: 18px;">
<label for="{forms[4]}_card_{sn}">Card number in HEX:</label>
<input type="text" id="{forms[4]}_card_{sn}" name="{forms[4]}_card" value="123456789ABC" form="{forms[4]}_{sn}">
</td>
<td style="width: 33.3333%; height: 18px;">
Delete card from a controller memory. Card number must be in HEX and contain 12 symbols (6 bytes).
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
Delete all cards stored in controller memory.
</td>
</tr>"""

    # Table end
    answer += """
</tbody>
</table>"""

    # Start event collapsible view
    DAY_TO_SHOW = 5
    start = datetime.now().date() - timedelta(DAY_TO_SHOW)  # The end of this day
    days = [datetime(start.year, start.month, start.day) + timedelta(i) for i in range(0, DAY_TO_SHOW + 2)]
    for day in range(0, DAY_TO_SHOW + 1):
        res = _get_events_by_date(['service_data/{}_events.db'.format(sn)], days[day], days[day + 1])
        if len(res) == 0:
            continue
        answer += '<button type="button" class="collapsible">{}</button>'.format(days[day].strftime('%d %b'))
        answer += '<div class="content">'
        for row in res:
            answer += '<div>At {} card {} event {}</div>'.format(
                datetime.fromtimestamp(int(row[0])).strftime('%H:%M:%S'), row[1], row[2]
            )
        answer += '</div>'
    return answer


def get_page(controllers_dict):
    head = """
<!DOCTYPE html>
<html lang="en">
<head>
<title>Z5R control</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset="UTF-8">
<style>
.collapsible {
  background-color: #777;
  color: white;
  cursor: pointer;
  padding: 5px;
  width: 100%;
  border: 2px solid #888;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.active, .collapsible:hover {
  background-color: #555;
}

.content {
  padding: 0 5px;
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}

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
<h1 style="text-align: center;">Z5R-Web server control</h1>
"""
    tail = """

<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
</script>

</body>
</html>
"""
    answer = head
    for sn in controllers_dict:
        answer += _per_controller_page(sn)
    answer += tail
    return answer
