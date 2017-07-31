import os
import csv
import re

from TwitterAPI import TwitterAPI

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN_KEY = os.environ['ACCESS_TOKEN_KEY']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

# calculate a number that im willing to live with -- 40% under the speed i pay for
ALLOWED_THRESHOLD = .40

# speed i pay for in bits
PAY_FOR = {
  'download': 300000000,
  'upload': 300000000
}

MESSAGE = """
@vodafone_es te pago por 300/300 porque me das {0:.2f}/{1:.2f}!?

la data esta aqui: https://github.com/kingbuzzman/vodafone_annoy
""".strip()


def filerev(somefile, buffer=0x20000):
    """
    Reads the file backwards (think tail)

    Thanks to Ignacio Vazquez-Abrams (https://stackoverflow.com/questions/2301789/read-a-file-in-reverse-order-using-python#answer-2301867)  # noqa
    I don't love it, i can see this working without the 're' -- but i didnt want to spend the time to fix it
    """
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
    """
    Send the tweet
    """
    api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

    with open('graph.png', 'rb') as image:
        data = image.read()
        request = api.request('statuses/update_with_media',
                              {'status': MESSAGE.format(download, upload)},
                              {'media[]': data})
        print('Sent.' if request.status_code == 200 else 'Error. ' + request.text)


def main():
    # open the csv file
    with open('vodafone.csv', 'rb') as csvfile:
        # read the very last line
        last_line = [next(filerev(csvfile))]
        # parse the very last line
        server_id, server_sponsor, server_name, timestamp, \
            server_d, ping, download, upload, wifi_name, router_ping = next(csv.reader(last_line, delimiter=','))

        # convert the values from str to float
        download = float(download)
        upload = float(upload)

        # calculate the minimun speed im willing to tolerate without bugging them about it (40% of my current speed)
        threshold_download = PAY_FOR['download'] - (PAY_FOR['download'] * ALLOWED_THRESHOLD)
        threshold_upload = PAY_FOR['upload'] - (PAY_FOR['upload'] * ALLOWED_THRESHOLD)

        # if what im willing to have is lower than what i have, annoy them!
        if threshold_download > download or threshold_upload > upload:
            annoy_vodafone(download / (1000**2), upload / (1000**2))


if __name__ == '__main__':
    main()
