#-*- coding: utf-8 -*-

from konlpy.tag import Komoran
from collections import Counter
from collections import defaultdict
from scipy.sparse import csr_matrix
import numpy as np
from sklearn.preprocessing import normalize
import http.client
import urllib.parse, urllib.request, urllib.error
import psycopg2
from dao import CRUD

komoran = Komoran()
def komoran_tokenize(sent):
    words = komoran.pos(sent, join=True)
    words = [w for w in words if ('/NN' in w or '/XR' in w or '/VA' in w or '/VV' in w)]
    return words

    

def scan_vocabulary(sents, tokenize, min_count=2):
    counter = Counter(w for sent in sents for w in tokenize(sent))
    counter = {w:c for w,c in counter.items() if c >= min_count}
    idx_to_vocab = [w for w, _ in sorted(counter.items(), key=lambda x:-x[1])]
    vocab_to_idx = {vocab:idx for idx, vocab in enumerate(idx_to_vocab)}
    return idx_to_vocab, vocab_to_idx

def cooccurrence(tokens, vocab_to_idx, window=2, min_cooccurrence=2):
    counter = defaultdict(int)
    for s, tokens_i in enumerate(tokens):
        vocabs = [vocab_to_idx[w] for w in tokens_i if w in vocab_to_idx]
        n = len(vocabs)
        for i, v in enumerate(vocabs):
            if window <= 0:
                b, e = 0, n
            else:
                b = max(0, i - window)
                e = min(i + window, n)
            for j in range(b, e):
                if i == j:
                    continue
                counter[(v, vocabs[j])] += 1
                counter[(vocabs[j], v)] += 1
    counter = {k:v for k,v in counter.items() if v >= min_cooccurrence}
    n_vocabs = len(vocab_to_idx)
    return dict_to_mat(counter, n_vocabs, n_vocabs)

def dict_to_mat(d, n_rows, n_cols):
    rows, cols, data = [], [], []
    for (i, j), v in d.items():
        rows.append(i)
        cols.append(j)
        data.append(v)
    return csr_matrix((data, (rows, cols)), shape=(n_rows, n_cols))

def word_graph(sents, tokenize=None, min_count=2, window=2, min_cooccurrence=2):
    idx_to_vocab, vocab_to_idx = scan_vocabulary(sents, tokenize, min_count)
    tokens = [tokenize(sent) for sent in sents]
    g = cooccurrence(tokens, vocab_to_idx, window, min_cooccurrence, verbose)
    return g, idx_to_vocab

def reqNaverApi(query, display, start, sort):
    conn = http.client.HTTPSConnection("openapi.naver.com")
    payload = ''
    headers = {
    'X-Naver-Client-Id': '3UzE2S8I3deRrlyriw4i',
    'X-Naver-Client-Secret': 'Q4LzBPZss4'
    }
    url = "/v1/search/news.json?query=" + urllib.parse.quote(query) + "&display=" + display + "&start=" + start + "&sort=" + sort
    
    conn.request("GET", url, payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
 
def main():
    db = CRUD()
    # print(db.readDB(schema='myschema',table='table',colum='ID'))
    # db.updateDB(schema='myschema',table='table',colum='ID', value='와우',condition='유동적변경')
    # db.deleteDB(schema='myschema',table='table',condition ="id != 'd'")

    #d = komoran_tokenize("야권 후보 단일화 시 누구를 지지하겠느냐’는 질문에는 43.5%가 안 후보를 택했다. 윤 후보를 지지하겠다는 응답은 32.7%였다. 단일화 시 경쟁력이 높은 후보로도 43.3%가 안 후보를 꼽았고, 윤 후보는 35.8%였다.전날 재구성된 국민의힘 선거대책위원회 관련 논란에는 응답자 52.6%가 ‘윤 후보의 책임이 크다’고 답했다. ‘이준석 대표의 책임이 크다’고 답한 비율은 25.5%였다. 특히 2030세대에서 윤 후보 책임론이 각각 63.4%, 66%로 높았다. 이번 대선의 성격에 대해서는 ‘정권교체를 위해 야권 후보가 당선돼야 한다’는 응답이 50.3%, ‘정권 재창출을 위해 여당 후보가 당선돼야 한다’는 의견이 36.5%를 기록했다. ‘잘 모름’ 응답은 4.1%였다. 이번 여론조사의 표본오차는 95% 신뢰수준이 ±3.1%포인트다. 자세한 내용은 중앙선거여론조사심의위원회나 알앤써치 홈페이지를 참조하면 된다.");
    #print(d) 
    reqNaverApi("\"침수사고발생\"", "100", "1", "sim")

if __name__ == '__main__':
    main()
    