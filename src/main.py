import json
import sys
import time
import uuid
from itertools import chain

import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# Use tensorflow 1 behavior to match the Universal Sentence Encoder
# examples (https://tfhub.dev/google/universal-sentence-encoder/2).
import tensorflow.compat.v1 as tf
import tensorflow_hub as hub
from elasticsearch.helpers import parallel_bulk, bulk
from time import sleep
import re
from elasticsearch.helpers import BulkIndexError

##### INDEXING #####
from src.config import serviceD, guideD, keys, model_path

url_mask = lambda service, typ: f'https://docs.aws.amazon.com/{service}/latest/{typ}'

url_service_mask = 'https://[\w.]+/([\w.-]+)/latest/([\w.-]+)/?'


def get_start_url(key):
    service, typ = key.split('/')
    url_start = url_mask(service, typ)

    text = requests.get(url_start).text
    _soup = BeautifulSoup(text, features="html.parser")

    mtag = _soup.find('meta', attrs={'http-equiv': "refresh"})
    if not mtag:
        if not url_start.endswith('.html') and not url_start.endswith('/'):
            url_start += '/'

        return url_start

    url_suff = re.search('URL=([\w.-]+)', mtag.attrs['content']).group(1)
    url_use = '/'.join((url_start, url_suff))

    if not url_use.endswith('.html') and not url_use.endswith('/'):
        url_use += '/'

    return url_use

def index_texts(json_path, es):
    print("Creating the 'docs' index.")
    client.indices.delete(index=INDEX_NAME, ignore=[404])

    with open(INDEX_FILE) as index_file:
        source = json.loads(index_file.read().strip())
        client.indices.create(index=INDEX_NAME, body=source)



    alldocs = 0
    counts = 0
    fails = 0
    infos = []
    errors = []
    for ikey, key in enumerate(keys):

        url_use = get_start_url(key)
        service, guidename = re.match(url_service_mask, url_use).group(1, 2)
        service = serviceD[service]
        guidename = guideD[guidename]

        with open(f'{json_path}/{service}_{guidename}.json', 'r') as f:
            elements_high = json.load(f)

        alldocs += len(elements_high)

        try:
            for success, info in parallel_bulk(es, gendata(INDEX_NAME, elements_high, ),
                                               raise_on_exception=False):
                if not success:
                    print('A document failed:', key, fails, end='     \r')
                    fails += 1
                    # infos.append(info)
                else:
                    print('success: ', ikey, len(keys), key, counts, alldocs, end='    \r')
                    counts += 1
        except BulkIndexError as be:
            errors.append(be)
            print('caught sth sth')

        if ikey % 8 == 7:
            sleep(60 * 2)
        # bulk(es, gendata('docs_chunks_v0.2',elements_high, ))

        # es.index(index="docs_chunks_v0.1", id=index_record, body=record)

        # print(ind,len(elements_high),service,guidename, index_record, end='     \r' )
        # break


def gendata(index, elements_high):
    pass
    just_texts = []
    for ind, record in enumerate(elements_high):
        pass
        # print(record)
        global_loc = [el['url'].split('/')[-1] for el in record['headers']]
        local_loc = [record[f'h{hlevel}']['urllink'] for hlevel in range(1, 7) if f'h{hlevel}' in record]
        headings_merge = '   \n'.join(chain(global_loc, local_loc))
        headings_merge = headings_merge.replace('-', '   ')
        headings_merge = headings_merge.replace('.html', '')
        headings_merge = headings_merge.replace('#', '')


        main_text = record['text']
        all_text = headings_merge+' \n '+main_text
        just_texts.append(all_text)

    vectors = embed_text(just_texts)
    for ind, (record, vector) in enumerate(zip(elements_high, vectors)):
        pass
        # print(record)
        global_loc = [el['url'].split('/')[-1] for el in record['headers']]
        local_loc = [record[f'h{hlevel}']['urllink'] for hlevel in range(1, 7) if f'h{hlevel}' in record]

        glocal_spot = '___'.join(chain(global_loc, local_loc))
        glocal_text = glocal_spot.replace('___', '    ')
        glocal_text = glocal_text.replace('-', '   ')
        glocal_text = glocal_text.replace('.html', '')
        glocal_text = glocal_text.replace('#', '')


        rands = str(uuid.uuid4())[:8]

        index_record = f"{record['aws_service']}_{record['aws_guide']}_{glocal_spot}__{record['container_type']}_{rands}"

        record['glocal_header'] = glocal_text
        # record['_id'] = index_record
        yield {"_index": index,
               '_id': index_record,
               '_op_type': 'index',
               'doc': record,
               'text_vector': vector,
               }






def index_batch(docs):
    titles = [doc["title"] for doc in docs]
    title_vectors = embed_text(titles)

    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME
        request["title_vector"] = title_vectors[i]
        requests.append(request)
    bulk(client, requests)

##### SEARCHING #####

def run_query_loop():
    while True:
        try:
            handle_query()
        except KeyboardInterrupt:
            return

def handle_query():
    query = input("Enter query: ")

    embedding_start = time.time()
    query_vector = embed_text([query])[0]
    embedding_time = time.time() - embedding_start

    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                # "source": "cosineSimilarity(params.query_vector, doc['text_vector_0.0']) + 1.0",
                "source": "doc['text_vector_0.0'].size() == 0 ? 0 : cosineSimilarity(params.query_vector, 'text_vector_0.0')",
                "params": {"query_vector": query_vector}
            }
        }
    }

    search_start = time.time()
    response = client.search(
        index=INDEX_NAME,
        # body={
        #     "size": SEARCH_SIZE,
        #     "query": script_query,
        #     "_source": {"includes": ["text", "main_header"]}
        # }
        query=script_query
    )
    search_time = time.time() - search_start

    print()
    print("{} total hits.".format(response["hits"]["total"]["value"]))
    print("embedding time: {:.2f} ms".format(embedding_time * 1000))
    print("search time: {:.2f} ms".format(search_time * 1000))
    for hit in response["hits"]["hits"]:
        print("id: {}, score: {}".format(hit["_id"], hit["_score"]))
        print(hit["_source"])
        print()

##### EMBEDDING #####

def embed_text(text):
    vectors = session.run(embeddings, feed_dict={text_ph: text})
    return [vector.tolist() for vector in vectors]

##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME = "docs_chunks_v0.14"
    INDEX_FILE = "data/posts/index2.json"

    DATA_FILE = "data/posts/posts.json"
    BATCH_SIZE = 1000

    SEARCH_SIZE = 20

    GPU_LIMIT = 0.5

    json_path = '/Users/kiks/Documents/awsdocs_proj/jsons' if len(sys.argv)<2 else sys.argv[1]

    print("Downloading pre-trained embeddings from tensorflow hub...")
    tf.compat.v1.disable_eager_execution()
    embed = hub.Module(model_path)
    text_ph = tf.placeholder(tf.string)
    embeddings = embed(text_ph)
    print("Done.")

    print("Creating tensorflow session...")
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = GPU_LIMIT
    session = tf.Session(config=config)
    session.run(tf.global_variables_initializer())
    session.run(tf.tables_initializer())
    print("Done.")

    client = Elasticsearch('http://localhost:9200')

    index_texts(json_path, client)
    # run_query_loop()

    print("Closing tensorflow session...")
    session.close()
    print("Done.")
