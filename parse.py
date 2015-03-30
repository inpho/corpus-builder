from codecs import open
import json
import rython
import xmlrpclib

ctx = rython.RubyContext(requires=["rubygems", "anystyle/parser"])
ctx("Encoding.default_internal = 'UTF-8'")
ctx("Encoding.default_external = 'UTF-8'")

anystyle = ctx("Anystyle.parser")

def parse_citations_from_file(readings_file):
    return_list = []
    with open(readings_file, 'r') as readfile:
        data = json.load(readfile)

    for d in data:
        d['original'] = d['original'].encode('utf-8')
        try:
            parsed = anystyle.parse(d['original'])[0]
            d['parsed'] = parsed
        except xmlrpclib.Fault:
            d['parsed'] = None
            print "could not parse", d['original']
    with open(readings_file, 'w') as outfile:
        json.dump(data, outfile)

parse_citations_from_file('tom.json')
