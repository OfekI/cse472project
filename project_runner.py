from os.path import abspath, exists, join, normpath
import requests
from json import loads

def parse_corpus(filename):
  in_doc = False
  in_p = False
  paragraphs = []
  
  with open(filename) as f:
    for line in f:
      if line.startswith('<DOC'):
        in_doc = True
        paragraphs.append([])
      elif line.startswith('</DOC>'):
        in_doc = False
      elif line.startswith('<P>'):
        in_p = True
      elif line.startswith('</P>'):
        in_p = False
      elif in_p:
        paragraphs[-1].append([line])
  print(paragraphs[0][0][0].replace(paragraphs[0][0][0][210:216], 'cause'))

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
  

def main():
  filename = 'nucle3.2.sgml'
  parse_corpus(filename)
  print(requests.post('http://localhost:8085',
                json={'params': ['This sentence might have contain error.',
                                 'This sentence might have some errors.'],
                      'id': 0,
                      'jsonrpc': '2.0',
                      'method': 'CorrDet'},
                headers={'content-type': 'text/plain'}).body)

main()