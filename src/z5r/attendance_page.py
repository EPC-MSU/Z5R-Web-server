from datetime import datetime
from datetime import timedelta
from .common import get_events_by_date, em_marine, get_users_list


DAY_TO_SHOW = 14


def get_attendance_page():
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
    start = datetime.now().date() - timedelta(DAY_TO_SHOW)  # The end of this day
    days = [datetime(start.year, start.month, start.day) + timedelta(i) for i in range(0, DAY_TO_SHOW + 2)]
    for day in range(0, DAY_TO_SHOW + 1):
        res = get_events_by_date(days[day], days[day + 1], card_filter=True)
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

        users_dict = get_users_list()

        work_periods = split_first_last(res)
        answer += '<button type="button" class="collapsible">{}</button>'.format(days[day].strftime('%d %b'))
        answer += '<table class="content">'
        answer += """<tr>
        <td>Name</td>
        <td>Card HEX</td>
        <td>Card Em-Marine</td>
        <td>First event</td>
        <td>Last event</td>
        </tr>"""

        for card in work_periods:
            if card in users_dict:
                name = users_dict[card]
            else:
                name = ''
            answer += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                name,
                card,
                em_marine(card),
                datetime.fromtimestamp(int(work_periods[card][0])).strftime('%H:%M:%S'),
                datetime.fromtimestamp(int(work_periods[card][1])).strftime('%H:%M:%S')
            )
        answer += '</table>'

    answer += tail
    return answer
