import requests
import os
import json
import sys
import urllib
from csv import DictReader, Sniffer


def csvs_from_envvar():
    json = os.environ.get("INPUT_JSON")
    if json is None:
        url = os.environ.get("INPUT_JSON_URL")
        json = requests.get(url).text
    config = json.loads(json)

    return [requests.get(url).text for url in config["file_relationships"]]

def csvs_from_argv():
    data = []
    for path in sys.argv[1:]:
        with open(path) as f:
            data.append(f.read())
    return data

def read_csvs(csvs, primary_key):
    list_of_lists_of_dicts = [
        list(DictReader(csv.splitlines(), dialect=Sniffer().sniff(csv)))
        for csv in csvs]
    key_sets = [list_of_dicts[0].keys()
                for list_of_dicts in list_of_lists_of_dicts]
    key_union = set()
    for s in key_sets:
        key_union.update(s)

    rows = [d  for l_of_d in list_of_lists_of_dicts for d in l_of_d]
    id_rows = [{**d, **{primary_key: i}} for (i, d) in enumerate(rows)]
    return {
        'header': sorted(key_union),
        'rows': id_rows
    }

def make_column_def(header):
    return [{'column': col, 'type': 'string'} for col in header]

def make_tsv(header, rows):
    header_line = '\t'.join(header)
    lines = [header_line]
    for row in rows:
        line = '\t'.join([row.get(h) or '' for h in header])
        lines.append(line)
    return '\n'.join(lines)

def make_outside_data_js(data, primary_key):
    column_def_json = json.dumps(make_column_def(data['header']))
    tsv_encoded = urllib.parse.quote(make_tsv(data['header'], data['rows']))
    return '''
var outside_data = [
  {{
    id: "data",
    name: "Data",
    desc: {{ separator:"\\t", primaryKey:"{}", columns:{} }},
    url: "data:text/plain;charset=utf-8,{}"
  }}
];
'''.format(primary_key, column_def_json, tsv_encoded)

if __name__ =="__main__":
    csvs = csvs_from_argv() if sys.argv[1:] else csvs_from_envvar()
    primary_key = 'id'
    data = read_csvs(csvs, primary_key)
    js = make_outside_data_js(data, primary_key)
    print(js)
