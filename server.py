import csv
import json
from StringIO import StringIO
"""
from vsm.corpus import Corpus
from vsm.model.beaglecomposite import BeagleComposite
from vsm.viewer.beagleviewer import BeagleViewer
from vsm.model.ldacgsmulti import LdaCgsMulti as LCM
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer as LDAViewer
"""
from bottle import response, route, run, static_file
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
    # parser.add_argument('k', type=int)
    args = parser.parse_args()
    # load_model(args.k)

    run(host='localhost', port=args.port)

