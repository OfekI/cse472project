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
                corr.strip() + paragraph[0][end_off:]
            paragraph.append((correction, m.find('TYPE').text.strip()))
    return paragraphs


def parse_corpus(filename):
    in_doc = False
    in_p = False
    docs = []

    with open(filename) as f:
        in_doc = False
        for line in f:
            if line.startswith('<DOC'):
                in_doc = True
                docs.append([])
            if in_doc:
                docs[-1].append(line)
            if line.startswith('</DOC>'):
                in_doc = False
                docs[-1] = parse_doc(docs[-1])
    return docs


def make_request(orig, corrected, t):
    response = requests.post('http://localhost:8085',
                             json={'params': [orig, corrected],
                                   'id': 0,
                                   'jsonrpc': '2.0',
                                   'method': 'CorrDet'},
                             headers={'content-type': 'text/plain'})
    error = loads(response.content)['result'][1]
    
    type_msgs = {'Vform': 'wrong verb form',
                 'Vt': 'wrong verb tense',
                 'SVA': 'verb agreement',
                 'Nn': 'wrong noun form',
                 'Prep': 'preposition needs replacing',
                #  'V0': '',
                #  'Mec': '',
                 }
    
    if t not in type_msgs or type_msgs[t] != error[2]:
        print(error)


def generate_sentence_pairs(sentences, limit):
    return [(s[0], *s[i])
            for p in sentences[0:limit]
            for s in p
            for i in range(1, len(s))][0:limit]


def main():
    filename = 'nucle3.2.sgml'
    sentences = parse_corpus(filename)
    for (s1, s2, t) in generate_sentence_pairs(sentences, int(sys.argv[1]) if len(sys.argv) == 2 else 10):
        make_request(s1, s2, t)


main()
