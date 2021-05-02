from flask import Flask, request, Response, send_file
from feedgen.feed import FeedGenerator
import requests
import re
import datetime

app = Flask(__name__)

headers = {
    'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}


@app.route('/')
def index():
    return "It works!"


@app.route('/download')
def download():
    board_id = request.args.get('b_id')
    item_id = request.args.get('id')

    if board_id is None or item_id is None:
        return "Parameter Error"

    view_url = "https://www.tfreeca22.com/board.php?mode=view&b_id={}&id={}&page=1"

    url = view_url.format(board_id, item_id)
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        regex = r"href=\"(https:\/\/www.filetender.com\/.*?)\""
        matches = re.finditer(regex, res.text, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):
            download_url = match.group(1)
            print("URL : " + download_url)

            header_referer = headers.copy()
            header_referer['Referer'] = view_url

            res = requests.get(download_url, headers=header_referer)
            if res.status_code == 200:
                header_referer['Referer'] = download_url
                return process_file(res.text, header_referer, item_id)


def process_file(html, new_headers, item_id):

    regex = r"<input .*? name=\"key\" value=\"(.*?)\">.*?<input .*? name=\"Ticket\" value=\"(.*?)\"\/>.*?<input .*? name=\"Randstr\" value=\"(.*?)\"\/>.*?<input .*? name=\"UserIP\" value=\"(.*?)\"\/>"
    matches = re.finditer(regex, html, re.DOTALL | re.MULTILINE)

    for matchNum, match in enumerate(matches, start=1):
        param_key = match.group(1)
        param_ticket = match.group(2)
        param_randstr = match.group(3)
        param_userip = match.group(4)

        last_url = "?key={}&Ticket={}&Randstr={}&UserIP={}".format(param_key, param_ticket, param_randstr, param_userip)

        regex2 = r"var newUrl = '(.*?)';"
        matches2 = re.finditer(regex2, html, re.DOTALL | re.MULTILINE)
        for matchNum2, match2 in enumerate(matches2, start=1):
            last_url = match2.group(1) + last_url

            r = requests.get(last_url, headers=new_headers, stream=True)

            return send_file(r.raw,
                             mimetype="application/x-bittorrent",
                             attachment_filename=item_id + ".torrent",
                             as_attachment=True
                             )

    return "Download Error", 500


@app.route('/rss')
def rss():

    board_id = request.args.get('b_id')
    sc = request.args.get('sc')

    if board_id is None or sc is None:
        return "Parameter Error"

    list_url = "https://www.tfreeca22.com/board.php?mode=list&b_id={}&sc={}"

    url = list_url.format(board_id, sc)
    res = requests.get(url, headers=headers)

    date = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))

    fg = FeedGenerator()

    fg.title('tfreeca RSS')
    fg.author({'name': 'David Choi', 'email': 'themars@gmail.com'})
    fg.link(href='https://www.tfreeca22.com/board.php?mode=list&b_id=' + board_id, rel='alternate')
    fg.subtitle('tfreeca feed rss')
    fg.language('ko')
    fg.lastBuildDate(date)

    if res.status_code == 200:
        regex = r"href=\"board\.php\?mode=view&b_id=" + board_id + "&id=(.*?)&sc=.*?&page=1\" class=\"stitle1\">(.*?)<span .*?</a>"
        matches = re.finditer(regex, res.text, re.DOTALL)
        for matchNum, match in enumerate(matches, start=1):
            item_id = match.group(1)
            item_title = match.group(2).strip()

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
    app.run(host="0.0.0.0", port=8881)
