'''
Takes a plaintext file of unparsed bibliography entries and parses them using
AnyStyle.io. Then performs a search for the title on the HathiTrust and returns
matching IDs. The final data is output as a JSON struct for use on the web,
particularly with the corpus builder tool at
http://github.com/inpho/corpus-builder

Run with 'python darparse.py -h' to see a list of command arguments.
'''
import json
import os.path
import subprocess
import tempfile
from time import sleep
from urllib.request import urlopen
from urllib.parse import quote_plus

def parse(ref):
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(bytes(ref, 'utf8'))
        tmp.flush()

        data = subprocess.check_output(f'anystyle -f json --stdout parse {tmp.name}', shell=True)
    try:
        return json.loads(data)[0]
    except IndexError:
        return None


def parse_citations_from_file(citation_file):
    return_list = []
    with open(citation_file) as readfile:
        for i, line in enumerate(readfile):
            line = line.strip()
            if line:
                parsed =  parse(line)
                return_list.append({'original' : line, 'parsed' : parsed})

    return return_list
         
def search(title, sleep_time=1):
    """ Queries the HTRC Solr index with a title and returns the resulting metadata.
    Documentation: http://www.hathitrust.org/htrc/solr-api
    """
    # TODO: Parameterize hostname	
    solr ="http://chinkapin.pti.indiana.edu:9994/solr/meta/select/?q=title:%s" % quote_plus(title)
    solr += "&wt=json" ## retrieve JSON results
    # TODO: exception handling
    try:
        data = json.load(urlopen(solr))
    except ValueError :
        print("No result found for " + title)
        return
    if sleep:
        sleep(sleep_time) ## JUST TO MAKE SURE WE ARE THROTTLED
    try:
        return data['response']['docs'][0]
    except IndexError:
        return None

def populate_htrc(citations):
    for citation in citations:
        citation['htrc_id'] = None
        citation['htrc_md'] = None
        if citation['parsed']:
            title = citation['parsed'].get('title')
            if title:
                title = title[0].replace("/", "")
                title = title.replace(":", "")
                title = title.replace("[", "")
                title = title.replace("]", "")
                htrc_md = search(title.encode('utf-8'))
            
                if htrc_md:
                    citation['htrc_md'] = htrc_md
                    citation['htrc_id'] = htrc_md.get('id')

    return citations

def extant_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.isfile(x):
        raise argparse.ArgumentError("%s does not exist" % x)
    return x

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-o', dest='output', help="output file", default=None)
    parser.add_argument('--citation_file', help="citation file", default="1860-1871-tofind.txt",
        type=extant_file)
    args = parser.parse_args()

    print("Parsing Citations...")
    citations = parse_citations_from_file(args.citation_file)

    print("Retrieving HTRC IDs...")
    citations = populate_htrc(citations)

    print("Printing output file...")
    while not args.output:
        args.output = raw_input("Output filename: www/").strip()
    if not args.output.startswith('www/'):
        args.output = 'www/' + args.output
    with open(args.output, 'wb') as output_file:
        json.dump(citations, output_file)

    print("TIP: launch Corpus Builder with:")
    print("python server.py -p 9024")
    print("\n")
    print("TIP: Navigate your browser to:")
    print("http://localhost:9024/?corpus="+args.output.replace('www/',''))
