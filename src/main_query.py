import csv
import functools
import json
import time
import uuid
from collections import defaultdict
from itertools import chain

import numpy as np
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
from src.config import serviceD, guideD, keys, all_queries, aws_categories, all_aws_services, model_path

##### SEARCHING #####
from src.html_exporter import make_combined_html_doc


def run_query_loop():
    while True:
        try:
            handle_query()
        except KeyboardInterrupt:
            return

def handle_query():
    query = input("Enter query: ")

    perform_query(query)


def perform_query(query, included_services='*'):
    embedding_start = time.time()
    query_vector = embed_text([query])[0]
    embedding_time = time.time() - embedding_start
    script_query = {
        "script_score": {
            "query": {"regexp": {
                "doc.aws_service": {
                    "value": included_services}}},
            "script": {
                # "source": "cosineSimilarity(params.query_vector, doc['text_vector_0.0']) + 1.0",
                "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }
    search_start = time.time()
    response = client.search(
        index=INDEX_NAME,
        body={
            "size": SEARCH_SIZE,
            "query": script_query,
            "_source": {"includes": ["doc.glocal_header","doc.text",
                                     "doc.main_url", "doc.aws_service"]}
        }
        # body=script_query
    )
    search_time = time.time() - search_start
    print()
    print("{} total hits.".format(response["hits"]["total"]["value"]))
    print("embedding time: {:.2f} ms".format(embedding_time * 1000))
    print("search time: {:.2f} ms".format(search_time * 1000))

    records = []


    for hit in response["hits"]["hits"]:
        # print("id: {}, score: {}".format(hit["_id"], hit["_score"]))

        records.append({**hit["_source"]['doc'], **{'score': [hit['_score']] } })

        # print(hit["_source"])
        # print()
    return records

##### EMBEDDING #####

def embed_text(text):
    vectors = session.run(embeddings, feed_dict={text_ph: text})
    return [vector.tolist() for vector in vectors]



####### Going Through topics #######

def search_collection_topic(do_save_csv=False):

    sep = "|"
    records = {}
    scores = []
    coverageD = defaultdict(dict)
    query2topic = {}
    scores_byRow = []
    for queries, aws_category, aws_services in zip(all_queries, aws_categories, all_aws_services):
        for qrow,qLine in enumerate(queries.splitlines()):
            if not qLine.strip():
                continue

            scores_byRow.append([])
            for query in qLine.split(sep):
                aws_subt_id = f"{aws_category}.{qrow} "
                query2topic[query] = aws_category, aws_subt_id
                coverageD[aws_category][aws_subt_id] = 0

                new_recs = map(lambda x: (x['glocal_header'], {**x, **{'exam_topic': [aws_category], 'query': []}}), perform_query(query, aws_services))
                for k, record_data in new_recs:
                    if k not in records:
                        records[k] = record_data
                    else:
                        records[k]['score'].extend(record_data['score'])
                        records[k]['exam_topic'].extend(record_data['exam_topic'])

                    records[k]['query'].append(query)
                    records[k]['num_occurances'] = len(records[k]['score'])
                    records[k]['avg_score'] = sum(records[k]['score'])/len(records[k]['score'])

                    scores.extend(records[k]['score'])
                    scores_byRow[-1].extend(records[k]['score'])

                # records.extend(map(lambda x: x['glocal_header']:{**x, **{'exam_topic': aws_category}},
                #                    perform_query(query, aws_services)))
    max_score = max([rec['avg_score'] for rec in records.values()])
    max_occurances = max([rec['num_occurances'] for rec in records.values()])
    for rec in records.values():
        rec['norm_score'] = (rec['avg_score']/max_score)+(rec['num_occurances']/max_occurances)

    for ll in scores_byRow:
        print( f'{(25,50,75,90,95,99)} ress:-  {np.percentile(ll,(25,50,75,90,95,99))} , {len(ll)}')

    rec_list = sorted(list(records.values()), key=lambda x: -x['norm_score'])
    for ind, rec in enumerate(rec_list):
        if ind%(len(rec_list)//10)==100:
            print(f'at {ind} record')
        for rscore, rquery in zip(rec['score'], rec['query']):
            cat,topic = query2topic[rquery]
            coverageD[cat][topic] += rscore
        sum_noncovered = 0
        for t in aws_categories:
            rec[t+'_noncovered'] = sum( (1 for q in coverageD[t].values() if q == 0))/len(coverageD[t])
            rec[t+'_avgsubt_score'] = sum(coverageD[t].values())/len(coverageD[t])
            sum_noncovered += rec[t+'_noncovered']

        rec['all_uncovered_avg'] = sum_noncovered/len(aws_categories)
        best_score_ind = np.argmax(rec['score'])
        rec['best_rated_subtopic'] = rec['query'][best_score_ind].strip()

    if do_save_csv:
        example_record = rec
        with open('aws_es_collection_links.csv', 'w') as f:
            w = csv.DictWriter(f, example_record.keys())
            w.writeheader()
            for rr in rec_list:
                w.writerow(rr)

    top_recs = rec_list[:1000].copy()
    top_recs.sort(key=lambda x: -x['norm_score'])

    for i in range(0, 1000, 100):
        top_recs[i:i+100] = sorted(top_recs[i:i+100], key=lambda x: (x['aws_service'], -x['norm_score'])  )

    links = [(r['main_url'], r['aws_service'], r['best_rated_subtopic']) for r in top_recs]
    make_combined_html_doc(links)


    #
    # with open("aws_es_collection_links.json", 'w') as f:
    #     f.write(json.dumps(records))
##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME = "docs_chunks_v0.14"

    BATCH_SIZE = 100000

    SEARCH_SIZE = 300

    GPU_LIMIT = 0.5

    print("Downloading pre-trained embeddings from tensorflow hub...")
    tf.compat.v1.disable_eager_execution()
    tf.compat.v1.enable_resource_variables()

    # The model can be downloaded from
    # https://tfhub.dev/google/universal-sentence-encoder/2?tf-hub-format=compressed
    embed = hub.KerasLayer(model_path)
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

    # index_texts(client)
    # run_query_loop()
    search_collection_topic()

    print("Closing tensorflow session...")
    session.close()
    print("Done.")
