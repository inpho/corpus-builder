import json
import os.path

def extract_ids(filename):
    with open(filename,'rb') as datafile:
        data = json.load(datafile)

    return [d['htrc_id'] for d in data if d.get('htrc_id')]

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
    parser.add_argument('inputfile', help="citation file", 
        type=extant_file)
    args = parser.parse_args()

    ids = extract_ids(args.inputfile)
    while not args.output:
        args.output = raw_input("Output filename: ").strip()
    with open(args.output, 'w') as outfile:
        outfile.writelines([id + '\n' for id in ids])
