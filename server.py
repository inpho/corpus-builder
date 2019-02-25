import csv
from datetime import datetime, timedelta
import json
from io import StringIO
"""
from vsm.corpus import Corpus
from vsm.model.beaglecomposite import BeagleComposite
from vsm.viewer.beagleviewer import BeagleViewer
from vsm.model.ldacgsmulti import LdaCgsMulti as LCM
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer as LDAViewer
"""
from bottle import request, response, route, run, static_file
"""
path = '/var/inphosemantics/data/20140801/sep/vsm-data/'

lda_c = Corpus.load(path + 'sep-nltk-freq1.npz')
lda_m = None
lda_v = None
def load_model(k):
    global lda_m, lda_v
    lda_m = LCM.load(path + 'sep-nltk-freq1-article-LDA-K%s.npz' % k)
    lda_v = LDAViewer(lda_c, lda_m)
"""

def _cache_date(days=0):
    time = datetime.now() + timedelta(days=days)
    return time.strftime("%a, %d %b %Y %I:%M:%S GMT")

@route('/write/<filename:path>', method='POST')
def write(filename):
    with open('www/' + filename, 'rb') as jsonfile:
        originaldata = json.load(jsonfile)

    data = [datum for datum in originaldata 
        if datum['original'] != request.POST['original'].decode('utf8')]

    with open('www/' + filename, 'wb') as jsonfile:
        request.POST['confirmed'] = True
        data.append(dict(request.POST.items()))
        print(data[-1])
        data = json.dumps(data)
        jsonfile.write(data)

    return "OK"

@route('/clear/<filename:path>', method='POST')
def clear(filename):
    with open('www/' + filename, 'rb') as jsonfile:
        originaldata = json.load(jsonfile)

    data = [datum for datum in originaldata 
        if datum['original'] != 
            request.POST['original'].decode('utf-8')]
    print(len(data), len(originaldata))

    with open('www/' + filename, 'wb') as jsonfile:
        request.POST['confirmed'] = True
        data.append(dict(request.POST.items()))
        print(data[-1])
        data = json.dumps(data)
        jsonfile.write(data)

    return "OK"

@route('/<filename>.json')
def send_static(filename):
    response.set_header('Expires', 0)
    response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.set_header('Pragma', 'no-cache')
    response.content_type = 'application/json; charset=UTF-8'
    f = open('www/'+filename+'.json', 'rb').read()
    return f

@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='www/')

@route('/')
def index():
    return send_static('index.html')

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=9020)
    args = parser.parse_args()

    run(host='', port=args.port)

