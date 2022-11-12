def users_handler(query, controllers_dict):
    pass


def get_users_page(controllers_dict):
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
    <h1 style="text-align: center;">Z5R-Web users page</h1>
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

    # Table start
    answer += """
    <form action="/users" id="users_form" method="get">
    <table style="width: 100%; height: 108px;">
    <tbody>"""

    answer += f"""
    <tr style="height: 18px;">
    <td style="width: 33.3333%; height: 18px;">
    <button name="action" type="submit" value="ttt">Set door params</button>
    </td>
    <td style="width: 33.3333%; height: 18px;">
    <label for="ttt_open">Open:</label>
    <input type="text" id="ttt_open" name="ttt_open" value="30"><br>
    <label for="ttt_open_control">Open control:</label>
    <input type="text" id="ttt_open_control" name="ttt_open_control" value="50">
    <br>
    <label for="ttt_close_control">Close control:</label>
    <input type="text" id="ttt_close_control" name="ttt_close_control" value="50">
    </td>
    <td style="width: 33.3333%; height: 18px;">
    Sets the time for opening and closing of the door. Open is time for opening door signal [1/10s].
    Open control is time of control for opened door [1/10s]). Close control is time of control for closing door [1/10s].
    </td>
    </tr>"""


    # Table end
    answer += """
    </tbody>
    </table>
    </form>"""

    answer += tail
    return answer
