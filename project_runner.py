import sys
from os.path import abspath, exists, join, normpath
import xml.etree.ElementTree as et
import requests
from json import loads


def parse_doc(doc):
    root = et.fromstring(''.join(doc))
    paragraphs = [[p.text.strip()] for p in root.find('TEXT').findall('P')]
    if root.find('ANNOTATION').find('MISTAKE').attrib['start_par'] is 0:
        def adjust(m): return int(m.attrib['start_par'])
    else:
        def adjust(m): return int(m.attrib['start_par']) - 1
    for m in root.iter('MISTAKE'):
        corr = m.find('CORRECTION').text
        if corr:
            paragraph = paragraphs[adjust(m)]
            start_off = int(m.attrib['start_off'])
            end_off = int(m.attrib['end_off'])
            correction = paragraph[0][:start_off] + \
                corr.strip() + paragraph[0][end_off + 1:]
            paragraph.append((correction, m.find('TYPE').text.strip()))
    return paragraphs


def parse_corpus(filename):
    in_doc = False
    in_p = False
    docs = []

    with open(filename) as f:
        for i, line in enumerate(f):
            if line.startswith('<DOC'):
                # print(i)
                docs.append([])
            docs[-1].append(line)
            if line.startswith('</DOC>'):
                docs[-1] = parse_doc(docs[-1])
            # elif line.startswith('<P>'):
            #   in_p = True
            # elif line.startswith('</P>'):
            #   in_p = False
            # elif in_p:
            #   paragraphs[-1].append([line])
        print(docs[0][0])

        # def load_cache():

        # def save_cache(cache):

        # def memoized_parse_corpus(filename):
        #   if exists('cache.out'):
        #     return load_cache()
        #   else:
        #     cache = parse_corpus(filename)
        #     save_cache(cache)
        #     return cache


def make_request(orig, corrected):
    response = requests.post('http://localhost:8085',
                             json={'params': [orig, corrected],
                                   'id': 0,
                                   'jsonrpc': '2.0',
                                   'method': 'CorrDet'},
                             headers={'content-type': 'text/plain'})
    json = loads(response.content)
    print(json['result'])


def generate_sentence_pairs(sentences, limit):
    [(s[0], *s[i])
     for i in range(1, len(s))
     for s in p
     for p in sentences[0:limit]][0:limit]


def main():
    filename = 'nucle3.2.sgml'
    sentences = parse_corpus(filename)
    for (s1, s2, _) in generate_sentence_pairs(sentences, int(sys.argv[1]) if len(sys.argv) == 2 else 10):
        make_request(s1, s2)

main()
