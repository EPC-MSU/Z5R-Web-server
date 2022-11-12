from datetime import datetime
from datetime import timedelta
from common import get_events_by_date


DAY_TO_SHOW = 5


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
    start = datetime.now().date() - timedelta(DAY_TO_SHOW)  # The end of this day
    days = [datetime(start.year, start.month, start.day) + timedelta(i) for i in range(0, DAY_TO_SHOW + 2)]
    databases = ['service_data/{}_events.db'.format(sn) for sn in controllers_dict]
    for day in range(0, DAY_TO_SHOW + 1):
        res = get_events_by_date(databases, days[day], days[day + 1], card_filter=True)
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

        def em_marine(card_hex):
            if len(card_hex) != 12:
                return 'N/A'
            if card_hex[0:6] != '000000':
                return 'N/A'
            return '{},{:05}'.format(int(card_hex[6:8], base=16), int(card_hex[8:12], base=16))

        work_periods = split_first_last(res)
        answer += '<button type="button" class="collapsible">{}</button>'.format(days[day].strftime('%d %b'))
        answer += '<table class="content">'
        answer += '<tr><td>Card HEX</td><td>Card Em-Marine</td><td>First event</td><td>Last event</td></tr>'
        for card in work_periods:
            answer += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                card,
                em_marine(card),
                datetime.fromtimestamp(int(work_periods[card][0])).strftime('%H:%M:%S'),
                datetime.fromtimestamp(int(work_periods[card][1])).strftime('%H:%M:%S')
            )
        answer += '</table>'

    answer += tail
    return answer
