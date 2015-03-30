from argparse import ArgumentParser
import time
import json
import sys

with open(sys.argv[-1]) as corpusfile:
    corpus = json.load(corpusfile)
    read = [entry for entry in corpus if entry.get('reading_date')]
    for entry in corpus:
        try:
            print entry['original']
            if not entry.get('reading_date'):
                entry['reading_date'] = raw_input("reading date:")
            print entry['reading_date']
        except (KeyboardInterrupt, SystemExit):
            break
        except:
            pass

    now_read = [entry for entry in corpus if entry.get('reading_date')]
    print "\n\nexiting", len(read), len(now_read)
    if len(read) != len(now_read):
        with open(sys.argv[-1] + '.%d' % time.time(), 'wb') as newfile:
            json.dump(corpus, newfile)
    sys.exit()
