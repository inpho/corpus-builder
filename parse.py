import json

new_data = []
count  = 0
with open('www/readings.json') as inputfile:
    data = json.load(inputfile)
    for datum in data:
        year = 0
        try:
            year = int(datum['htrc_md']['publishDateRange'][0])
        except:
            pass

        if year > 1862:
            datum['confirmed'] = False
            print datum['htrc_id']
            count += 1
        
        new_data.append(datum)
print count
with open('www/readings2.json', 'wb') as outputfile:
    json.dump(new_data, outputfile)
