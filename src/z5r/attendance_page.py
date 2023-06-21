from datetime import datetime
from datetime import timedelta
from .common import em_marine
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
      padding: 5px;
      spacing: 5px;
      text-align: center
    }

    div {
      padding: 5px;
    }
    </style>
    </head>
    <body>
    <h1 style="text-align: center;">Z5R-Web general attendance</h1>
    <div border="dotted" font-size="10px">
    <a href="/attendance_filter">Attendance by filter</a>
    </div>
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
    start = datetime.now().date() - timedelta(DAY_TO_SHOW-1)  # The end of this day
    days = [datetime(start.year, start.month, start.day) + timedelta(i) for i in range(0, DAY_TO_SHOW)]
    for day in days:
        dbcon = DbZ5R()
        users_cards = dbcon.get_reg_user_card_events_per_day(day)
        free_cards = dbcon.get_free_reg_cards_events_per_day(day)
        un_cards = dbcon.get_unregistered_cards_events_per_day(day)

        answer += '<button type="button" class="collapsible">{}</button>'.format(day.strftime('%d %b'))
        answer += '<table class="content">'
        answer += """<tr>
        <th>Name</th>
        <th>Card HEX</th>
        <th>Card Em-Marine</th>
        <th>First event</th>
        <th>Last event</th>
        </tr>"""

        for card in users_cards:
            answer += '<tr><td style="text-align:left">{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                card[0],
                card[1],
                em_marine(card[1]),
                card[2],
                card[3]
                )
        for card in free_cards:
            answer += '<tr><td style="text-align:left>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                '[Резерв]',
                int(card[0]),
                em_marine(card[0]),
                card[1],
                card[2]
            )
        for card in un_cards:
            answer += '<tr><td style="text-align:left>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                '[Не зарегистрирована]',
                card[0],
                em_marine(card[0]),
                card[1],
                card[2]
            )
        answer += '</table>'

    answer += tail
    return answer
