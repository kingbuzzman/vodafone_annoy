import os
import csv
import re

from TwitterAPI import TwitterAPI

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN_KEY = os.environ['ACCESS_TOKEN_KEY']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

ALLOWED_THRESHOLD = .40

PAY_FOR = {
  'download': 300000000,
  'upload': 300000000
}

MESSAGE = """
@vodafone_es te pago por 300/300 porque me das {0:.2f}/{0:.2f}!?

la data esta aqui: https://github.com/kingbuzzman/vodafone_annoy
""".strip()


def filerev(somefile, buffer=0x20000):
    somefile.seek(0, os.SEEK_END)
    size = somefile.tell()
    lines = ['']
    rem = size % buffer
    pos = max(0, (size // buffer - 1) * buffer)
    while pos >= 0:
        somefile.seek(pos, os.SEEK_SET)
        data = somefile.read(rem + buffer) + lines[0]
        rem = 0
        lines = re.findall('[^\n]*\n?', data)
        ix = len(lines) - 2
        while ix > 0:
            yield lines[ix]
            ix -= 1
        pos -= buffer
    else:
        yield lines[0]


def annoy_vodafone(download, upload):
    api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

    with open('graph.png', 'rb') as image:
        data = image.read()
        request = api.request('statuses/update_with_media',
                              {'status': MESSAGE.format(download, upload)},
                              {'media[]': data})
        print('Sent.' if request.status_code == 200 else 'Error.')


def main():
    with open('vodafone.csv', 'rb') as csvfile:
        last_line = [next(filerev(csvfile))]
        server_id, server_sponsor, server_name, timestamp, \
            server_d, ping, download, upload, wifi_name, router_ping = next(csv.reader(last_line, delimiter=','))

        download = float(download)
        upload = float(upload)

        threshold_download = PAY_FOR['download'] - (PAY_FOR['download'] * ALLOWED_THRESHOLD)
        threshold_upload = PAY_FOR['upload'] - (PAY_FOR['upload'] * ALLOWED_THRESHOLD)

        if threshold_download > download or threshold_upload > upload:
            annoy_vodafone(download / (1000**2), upload / (1000**2))


if __name__ == '__main__':
    main()
