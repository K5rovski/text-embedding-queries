import json
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
from src.config import serviceD, guideD, keys


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
            "_source": {"includes": ["doc.glocal_header", "doc.main_header",'doc.text']}
        }
        # body=script_query
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

    print("Downloading pre-trained embeddings from tensorflow hub...")
    tf.compat.v1.disable_eager_execution()
    embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder/2")
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
    run_query_loop()

    print("Closing tensorflow session...")
    session.close()
    print("Done.")
