# A simple client for querying driven by user input on the command line.  Has hooks for the various
# weeks (e.g. query understanding).  See the main section at the bottom of the file
from opensearchpy import OpenSearch
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import argparse
import json
import os
from getpass import getpass
from urllib.parse import urljoin
import pandas as pd
import fileinput
import logging
#import fasttext
from sentence_transformers import SentenceTransformer

sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')

# expects clicks and impressions to be in the row
def create_prior_queries_from_group(
        click_group):  # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    if click_group is not None:
        for item in click_group.itertuples():
            try:
                click_prior_query += "%s^%.3f  " % (item.doc_id, item.clicks / item.num_impressions)

            except KeyError as ke:
                pass  # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query


# expects clicks from the raw click logs, so value_counts() are being passed in
def create_prior_queries(doc_ids, doc_id_weights,
                         query_times_seen):  # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    click_prior_map = ""  # looks like: '1065813':100, '8371111':809
    if doc_ids is not None and doc_id_weights is not None:
        for idx, doc in enumerate(doc_ids):
            try:
                wgt = doc_id_weights[doc]  # This should be the number of clicks or whatever
                click_prior_query += "%s^%.3f  " % (doc, wgt / query_times_seen)
            except KeyError as ke:
                pass  # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query


# Given a list of (category, confidence) it will create an array of `match` query predicates
def create_category_matches(categories, boost=100):
    matches = [] # we will accumulate all "match" queries in here

    for cat, conf in categories:
        cat = cat[9:] # remove __label__
        print("Categ:", cat, "Conf:", round(conf,2))
        q = { 
            "match": {
                "categoryPathIds.keyword": { 
                    "query": cat,
                    "boost": boost*conf
                    }
                }
            }
        matches.append(q)
    print("\n")
    return matches



# Hardcoded query here.  Better to use search templates or other query config.
# TODO: `filter` is masking the reserved word. Rename it
def create_query(user_query, click_prior_query, filters, sort="_score", sortDir="desc", size=10, source=None,
                 use_synonyms=False, categories=[], filter=False):

    name_field = 'name.synonyms' if use_synonyms  else 'name'

    query_obj = {
        'size': size,
        "track_total_hits": True,
        "sort": [
            {sort: {"order": sortDir}}
        ],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [

                        ],
                        "should": [  #
                            {
                                "match": {
                                    name_field: {
                                        "query": user_query,
                                        "fuzziness": "1",
                                        "prefix_length": 2,
                                        # short words are often acronyms or usually not misspelled, so don't edit
                                        "boost": 0.01
                                    }
                                }
                            },
                            {
                                "match_phrase": {  # near exact phrase match
                                    "name.hyphens": {
                                        "query": user_query,
                                        "slop": 1,
                                        "boost": 50
                                    }
                                }
                            },
                            {
                                "multi_match": {
                                    "query": user_query,
                                    "type": "phrase",
                                    "slop": "6",
                                    "minimum_should_match": "2<75%",
                                    "fields": [f"{name_field}^10", "name.hyphens^10", "shortDescription^5",
                                               "longDescription^5", "department^0.5", "sku", "manufacturer", "features",
                                               "categoryPath"]
                                }
                            },
                            {
                                "terms": {
                                    # Lots of SKUs in the query logs, boost by it, split on whitespace so we get a list
                                    "sku": user_query.split(),
                                    "boost": 50.0
                                }
                            },
                            {  # lots of products have hyphens in them or other weird casing things like iPad
                                "match": {
                                    "name.hyphens": {
                                        "query": user_query,
                                        "operator": "OR",
                                        "minimum_should_match": "2<75%"
                                    }
                                }
                            }
                        ],
                        "minimum_should_match": 1,
                        "filter": filters  #
                    }
                },
                "boost_mode": "multiply",  # how _score and functions are combined
                "score_mode": "sum",  # how functions are combined
                "functions": [
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankShortTerm"
                            }
                        },
                        "gauss": {
                            "salesRankShortTerm": {
                                "origin": "1.0",
                                "scale": "100"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankMediumTerm"
                            }
                        },
                        "gauss": {
                            "salesRankMediumTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankLongTerm"
                            }
                        },
                        "gauss": {
                            "salesRankLongTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "script_score": {
                            "script": "0.0001"
                        }
                    }
                ]

            }
        }
    }
    # get the nested "bool" query from the function score
    bool_query = query_obj["query"]["function_score"]["query"]["bool"]
    if click_prior_query is not None and click_prior_query != "":
        bool_query["should"].append({
            "query_string": {
                # This may feel like cheating, but it's really not, esp. in ecommerce where you have all this prior data,  You just can't let the test clicks leak in, which is why we split on date
                "query": click_prior_query,
                "fields": ["_id"]
            }
        })
    if user_query == "*" or user_query == "#":
        # replace the bool
        try:
            query_obj["query"] = {"match_all": {}}
        except:
            print("Couldn't replace query for *")
    if source is not None:  # otherwise use the default and retrieve all source
        query_obj["_source"] = source

    if not categories:
        # if there are not categories, don't manipulte the query further
        return query_obj
    
    cat_matches = create_category_matches(categories, boost=20)

    if filter:
        # if filtering use a `filter` query
        bool_query["filter"] = cat_matches
    else:
        # Add the new clauses the existing `should` query. The "minimum_should_match"
        # option should ensure that it will not make filtering any stricter, just boosting
        bool_query['should'] += cat_matches
    return query_obj


def create_vector_query(user_query, size=10):
    user_query_vector = sentence_model.encode(user_query)
    q = {
        "size": size,
        "query": {
        "knn": {
        "name_emb": {
            "vector": user_query_vector,
            "k": size
            }
        }
        }
    }

    return q


# returns a list of pairs of (category, confidence)
def predict_categories(query, model, conf_threshold=.1, max_k=5):
    if not model:
        return []
    preds = model.predict(query, k=max_k)
    # transpose fastext output to create pairs of (label, confidence)
    labels_and_weights = zip(*preds)

    # return only the pairs with a confidence higher than conf_threshold
    return list(
        filter(lambda p: p[1]> conf_threshold, labels_and_weights)
    )


def search(client, user_query, index="bbuy_products", sort="_score", sortDir="desc", use_synonyms=False, 
            text_only=False, categories=[], filter=False, vector_search=False):
    #### W3: classify the query
    #### W3: create filters and boosts
    # Note: you may also want to modify the `create_query` method above
    query_obj = create_query(user_query, click_prior_query=None, filters=None, sort=sort, sortDir=sortDir, source=["name", "shortDescription"], 
                            use_synonyms=use_synonyms, categories=categories, filter=filter)

    # over-write `query_obj` if vector search
    if vector_search:
        query_obj=create_vector_query(user_query)

    logging.info(query_obj)
    response = client.search(query_obj, index=index)
    total_hits = response['hits']['total']['value']
    print("Total Hits: ", total_hits, "\n")
    if response and response['hits']['hits'] and len(response['hits']['hits']) > 0:
        hits = response['hits']['hits']
        if text_only:
            for h in hits:
                # Print in a readable form
                h = h["_source"]
                #print("Name:\t｜", h.get('name',[])[0])
                print(h.get('name',[])[0])
                descr = h['shortDescription']
                if descr:
                    #print("Descr:\t｜", descr[0][:80], "\n", "-"*90)
                    pass
        else:
            print(json.dumps(response, indent=2))


if __name__ == "__main__":
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
    parser = argparse.ArgumentParser(description='Build LTR.')
    general = parser.add_argument_group("general")
    general.add_argument("-i", '--index', default="bbuy_products",
                         help='The name of the main index to search')
    general.add_argument("-s", '--host', default="localhost",
                         help='The OpenSearch host name')
    general.add_argument("-p", '--port', type=int, default=9200,
                         help='The OpenSearch port')
    general.add_argument('--user',
                         help='The OpenSearch admin.  If this is set, the program will prompt for password too. If not set, use default of admin/admin')
    general.add_argument('--synonyms', action='store_true', help='Use "name.synonyms" instead of "name"')
    general.add_argument('-q', '--query', required=True, help='the text query to search in ES')
    general.add_argument('-t', '--text-only', action="store_true", help="keep only text from response JSON")
    general.add_argument('--ft-model', help="The binary fasttext model file")
    general.add_argument('--filter-categories', action="store_true", help="filter instead of boosting")
    general.add_argument('-v', '--vector-search', action="store_true", help="use vector search")


    args = parser.parse_args()

    if len(vars(args)) == 0:
        parser.print_usage()
        exit()

    host = args.host
    port = args.port
    use_synonyms = args.synonyms
    if args.user:
        password = getpass()
        auth = (args.user, password)

    base_url = "https://{}:{}/".format(host, port)
    opensearch = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        # client_cert = client_cert_path,
        # client_key = client_key_path,
        use_ssl=True,
        verify_certs=False,  # set to true if you have certs
        ssl_assert_hostname=False,
        ssl_show_warn=False,

    )
    index_name = args.index

    fasttext_model = fasttext.load_model(args.ft_model) if args.ft_model else None

    # create a list of categories and confidences
    category_pairs = predict_categories(args.query, fasttext_model)

    # serch prints the response
    search(
        client=opensearch, 
        user_query=args.query, 
        index=index_name, 
        use_synonyms=use_synonyms,
        text_only=args.text_only,
        filter=args.filter_categories,
        categories=category_pairs,
        vector_search=args.vector_search,
    )