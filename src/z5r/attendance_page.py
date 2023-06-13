from datetime import datetime
from datetime import timedelta
from .common import get_events_by_date, em_marine, get_users_list
from .dbz5r import DbZ5R


DAY_TO_SHOW = 21


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

        dbcon = DbZ5R()
        users_cards = dbcon.get_reg_user_card_events_per_day(day)
        free_cards = dbcon.get_free_reg_cards_events_per_day(day)
        un_cards = dbcon.get_unregistered_cards_events_per_day(day)

        answer += '<button type="button" class="collapsible">{}</button>'.format(days[day].strftime('%d %b'))
        answer += '<table class="content">'
        answer += """<tr>
        <td>Name</td>
        <td>Card HEX</td>
        <td>Card Em-Marine</td>
        <td>First event</td>
        <td>Last event</td>
        </tr>"""

        for card in users_cards:
            answer += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                card[0],
                int(card[1], 16),
                em_marine(int(card[1], 16)),
                datetime.fromtimestamp(card[2]).strftime('%H:%M:%S'),
                datetime.fromtimestamp(card[3]).strftime('%H:%M:%S')
                )
        for card in free_cards:
            answer += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                '',
                int(card[0], 16),
                em_marine(int(card[0], 16)),
                datetime.fromtimestamp(card[1]).strftime('%H:%M:%S'),
                datetime.fromtimestamp(card[2]).strftime('%H:%M:%S')
            )
        for card in un_cards:
            answer += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                '[Unregistered]',
                int(card[0], 16),
                em_marine(int(card[0], 16)),
                datetime.fromtimestamp(card[1]).strftime('%H:%M:%S'),
                datetime.fromtimestamp(card[2]).strftime('%H:%M:%S')
            )
        answer += '</table>'

    answer += tail
    return answer
