'''
Takes a plaintext file of unparsed bibliography entries and parses them using
AnyStyle.io. Then performs a search for the title on the HathiTrust and returns
matching IDs. The final data is output as a JSON struct for use on the web,
particularly with the corpus builder tool at
http://github.com/inpho/corpus-builder

Run with 'python darparse.py -h' to see a list of command arguments.
'''
import asyncio
import concurrent.futures
import json
import os.path
import subprocess
import tempfile
from time import sleep
from urllib.request import urlopen
from urllib.parse import quote_plus
from unidecode import unidecode

from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

HTRC_MD_FIELDS_TO_REMOVE = [
    'issuance',
    'subjectOccupation',
    'genre',
    'governmentDocument',
    'schemaVersion',
    'dateCreated',
    'classification',
    'subjectGeographic',
    'sourceInstitution',
    'subjectCartographics',
    'lccn',
    'rightsAttributes',
    'lastUpdateDate',
    'typeOfResource',
    'subjecttitleInfo',
    'subjectName',
    'accessProfile',
    'sourceInstitutionRecordNumber',
    'htBibUrl',
    'subjectTopic',
    'subjectTemporal',
    'pubPlace',
    'bibliographicFormat',
    'enumerationChronology',
    'subjectGenre',
    'pubDateSource',
    '_id'
]

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

client = AsyncIOMotorClient('192.168.1.168', 27017)
async def search(title, sleep_time=1, client=None):
    """ Queries the HTRC Solr index with a title and returns the resulting metadata.
    Documentation: http://www.hathitrust.org/htrc/solr-api
    """

    db = client.htrc
    collection = db.metadata

    title = unidecode(title)
    print(f"searching for '{title}'")
    document = await collection.find_one({'$text': {'$search' : title }},
                             {'score': {'$meta' : 'textScore'}},
                             sort=[('score', {'$meta' : 'textScore'})])

    for field in HTRC_MD_FIELDS_TO_REMOVE:
        try:
            del document[field]
        except KeyError:
            pass

    return document

async def populate_htrc(citations):
    futures = []
    for citation in citations:
        citation['htrc_id'] = None
        citation['htrc_md'] = None
        if citation['parsed']:
            title = citation['parsed'].get('title')
            authors = citation['parsed'].get('author')
            author = None
            if authors:
                author = ' '.join(authors[0].values())
            if title:
                title = title[0].replace("/", "")
                title = title.replace(":", "")
                title = title.replace("[", "")
                title = title.replace("]", "")
                if author:
                    title += ' ' + author
                futures.append(search(title, client=client))
                

    for f in futures:
        data = await f
        citation['htrc_md'] = data
        citation['htrc_id'] = citation['htrc_md']['volumeId']

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
    parser.add_argument('--citation_file', help="citation file", default="1860-part2.txt",
        type=extant_file)
    args = parser.parse_args()

    print("Parsing Citations...")
    citations = parse_citations_from_file(args.citation_file)

    print("Retrieving HTRC IDs...")
    loop = asyncio.get_event_loop()
    citations = loop.run_until_complete(populate_htrc(citations))

    print("Printing output file...")
    while not args.output:
        args.output = input("Output filename: www/").strip()
    if not args.output.startswith('www/'):
        args.output = 'www/' + args.output
    with open(args.output, 'w') as output_file:
        json.dump(citations, output_file)

    print("TIP: launch Corpus Builder with:")
    print("python server.py -p 9024")
    print("\n")
    print("TIP: Navigate your browser to:")
    print("http://localhost:9024/?corpus="+args.output.replace('www/',''))
