import datetime
import re

import requests
from feedgen.feed import FeedGenerator
from flask import Flask, request, Response, send_file

from download import Download

app = Flask(__name__)


def clean_html(raw_html):
    clean_text = re.sub(re.compile('<.*?>'), '', raw_html)
    return clean_text


@app.route('/')
def index():
    return "It works!"


@app.route('/download')
def download():

    board_id = request.args.get('b_id')
    item_id = request.args.get('id')

    if board_id is None or item_id is None:
        return "Parameter Error"

    return Download(b_id=board_id, id=item_id).start()


@app.route('/rss')
def rss():

    board_id = request.args.get('b_id')
    sc = request.args.get('sc')

    if board_id is None or sc is None:
        return "Parameter Error"

    params = {"mode": "list", "b_id": board_id, "sc": sc}
    url = "https://www.tfreeca22.com/board.php"

    res = requests.get(url, params=params, headers=headers)
    date = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))

    fg = FeedGenerator()

    fg.title('tfreeca RSS')
    fg.author({'name': 'David Choi', 'email': 'themars@gmail.com'})
    fg.link(href=res.url, rel='alternate')
    fg.subtitle('tfreeca feed rss')
    fg.language('ko')
    fg.lastBuildDate(date)

    if res.status_code == 200:
        regex = r"href=\"board\.php\?mode=view&b_id=" + board_id + "&id=(.*?)&sc=.*?&page=1\" class=\"stitle[0-9]\">(.*?) </a>"
        matches = re.finditer(regex, res.text, re.DOTALL)
        for matchNum, match in enumerate(matches, start=1):
            item_id = match.group(1)
            item_title = clean_html(match.group(2).strip())

            link = 'https://www.tfreeca22.com/board.php?mode=view&b_id=' + board_id + '&id=' + item_id + '&page=1'
            download_link = request.host_url + 'download?b_id=' + board_id + '&id=' + item_id

            fe = fg.add_entry()
            fe.id(link)
            fe.title(item_title)
            fe.link(href=download_link)
            fe.pubDate(date)

    rss_feed = fg.rss_str(pretty=True)

    r = Response(response=rss_feed, status=200, mimetype="application/xml")
    r.headers["Content-Type"] = "text/xml; charset=utf-8"

    return r


if __name__ == '__main__':
    app.run(host="0.0.0.0",
            port=8881,
            debug=False
            )
