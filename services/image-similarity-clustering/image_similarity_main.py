# http://10.104.1.144:3003/api/socialMediaPosts/count?[where][timestamp_ms][between][0]=1469644000000&[where][timestamp_ms][between][1]=1469644050000&filter[where][lang]=en

# http://10.104.1.144:3003/api/socialMediaPosts?filter[where][timestamp_ms][between][0]=1469695563000&filter[where][timestamp_ms][between][1]=1469702566000&filter[where][lang]=en&filter[limit]=5&filter[skip]=0
# to test:
    #from the redis cli run these commands
    #hmset 1 "state" "new" "similarity_threshold" .5 "similarity_method" "custom" "query_url" "http://10.104.1.144:3003/api/socialMediaPosts/" "lang" "en" "data_type" "text" "start_time_ms" 1469695563000 "end_time_ms" 1469702566000
    #hmset 1 "state" "new" "similarity_threshold" .5 "es_host" "54.234.139.42" "similarity_method" "custom" "es_port" "9200" "es_index" "stream" "es_doc_type" "jul2016-uk" "es_query" "{\"fields\":[\"timestamp_ms\",\"features\",\"id\"],\"query\":{\"bool\":{\"must\":{\"term\":{\"features\":0}},\"filter\":{\"range\":{\"timestamp_ms\":{\"gte\":\"1468617997000\",\"lt\":\"1468618897000\"}}}}}}"
    #publish similarity 1

import sys, os
import json
from image_similarity import ImageSimilarity
sys.path.append(os.path.join(os.path.dirname(__file__), "../util"))
from redis_dispatcher import Dispatcher
from loopy import Loopy


def process_message(key, job):
    # get features:
    print 'FINDING SIMILARITY'
    # do the work to find similarity
    image_similarity = ImageSimilarity(float(job['similarity_threshold']), job['similarity_method'])
    loopy = Loopy(job['query_url'], [
            {
                "query_type": "between",
                "property_name": "timestamp_ms",
                "query_value": [1469695563000, 1469702566000]
            },
            {
                "query_type": "where",
                "property_name": "lang",
                "query_value": "en"
            }
        ])

    total = loopy.get_count()
    print total
    # process initial results
    # for doc in data['hits']['hits']:
    #     image_similarity.process_vector(doc['fields']['id'][0], doc['fields']['features'])

    # sid = data['_scroll_id']
    # scroll_size = data['hits']['total']
    # while scroll_size > 0:
    #     print "Scrolling..."
    #     data = es.scroll(scroll_id=sid, scroll='2m')
    #     # Update the scroll ID
    #     sid = data['_scroll_id']
    #     # Get the number of results that we returned in the last scroll
    #     scroll_size = len(data['hits']['hits'])
    #     print "scroll size: " + str(scroll_size)
    #     # Do something with the obtained page
    #     for doc in data['hits']['hits']:
    #         image_similarity.process_vector(doc['fields']['id'][0], doc['fields']['features'])

    # print 'FINISHED SIMILARITY PROCESSING'
    # job['data'] = image_similarity.to_json()
    # job['state'] = 'processed'


if __name__ == '__main__':
    dispatcher = Dispatcher(redis_host='redis',
                            process_func=process_message,
                            channels=['genie::clust_txt', 'genie::clust_img'])
    dispatcher.start()

