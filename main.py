import os
import json
import uuid
import threading
from flask import Flask, request, Response
from azure.storage.table import TableService
from azure.storage.blob import BlockBlobService
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

app = Flask(__name__)

_env = os.environ
_storage_account = _env["STORAGE_ACCOUNT"] 
_storage_key = _env["STORAGE_KEY"] 

results = {}
def lda(jobid, docs):

    print "Starting job: %s" % jobid

    tf_vectorizer = CountVectorizer(
        max_df = 0.95, min_df = 2, max_features = 1000, stop_words='english'
    )

    tf = tf_vectorizer.fit_transform(docs)
    tf_feature_names = tf_vectorizer.get_feature_names()

    # This is the number of topics we are going to search 
    # for. We'll *always* find as many topics as we look for
    no_topics = 10

    lda = LatentDirichletAllocation(
        n_topics = no_topics, 
        max_iter = 5, 
        learning_method = 'online', 
        learning_offset = 50.,
        random_state = 0).fit(tf)

    # This is number of significant words we're going to write into the 
    # results
    no_top_words = 3 

    topics = []
    # LDA is now complete, get a list of lists of words
    for topic_idx, topic in enumerate(lda.components_):
        topics.append([tf_feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]])
    results[jobid] = topics

    print topics

    # Write the results into the job table
    table_service = TableService(account_name=_storage_account, account_key=_storage_key)
    task = {'PartitionKey': 'lda_jobs', 'RowKey': jobid, 'status' : 'completed', 'results' : str(results[jobid]) }
    table_service.update_entity('ldajobs', task)

    print "completed jobid: %s" % jobid


@app.route('/', methods = ["GET", "POST"])
def main():
    blob_container = request.json["container"]
    blob_id = request.json["id"]

    # Load up the .json from blob service
    blob_service = BlockBlobService(account_name=_storage_account, account_key=_storage_key)
    blob = blob_service.get_blob_to_text(blob_container, blob_id)

    # verbatims is a list of strings
    verbatims = json.loads(blob.content)

    # Generate a UUID for this job, since it's going to be a long running task
    # we're going to return the id to the caller and track job status is the table 'ldajobs'
    jobid = str(uuid.uuid4())

    # Create the table row for this job, initially status is 'started'
    table_service = TableService(account_name=_storage_account, account_key=_storage_key)
    table_service.create_table("ldajobs")
    task = {'PartitionKey': 'lda_jobs', 'RowKey': jobid, 'status' : 'started'}
    table_service.insert_entity('ldajobs', task)

    # Actually start the job
    threading.Thread(target = lda, args=(jobid, verbatims,)).start()

    # .. and immediately return the jobid to the caller
    return Response("%s verbatims now processing" % len(verbatims), status=200, mimetype='plain/text')

if __name__ == '__main__':
  app.run()
