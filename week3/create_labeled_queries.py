import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
from collections import defaultdict

# Useful if you want to perform stemming.
import nltk
stemmer = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/fasttext/labeled_queries.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

def normalize_text(txt):
    txt = txt.lower()
    # TODO: more text normalization
    return txt


def compute_category_counts(categories: pd.Series, ancestors: dict):
    cat_counts = defaultdict(int)
    for category in categories:
        # update for the leaf category and all its ancestors
        while category is not None:
            # update the current category count
            cat_counts[category] += 1
            # replace `category` with its ancestor
            category = ancestors.get(category)
    return cat_counts

def rollup_categories(categories: pd.Series, min_queries: int, ancestors: dict):
    """
    Given a series of categories, a min_count and a mapping of ancestors, it computes the # of queries per category
    (including ancestors). Using that, it and tries to map each given category to its ancestor with a count>min_count
    """
    cat_counts = compute_category_counts(categories, ancestors)

    def find_ancestor_with_min_count(category):
        """This is a nested helper function: For a given category, it will try to find an 
        ancestor with a count >= min_queries. Return None otherwise"""
        cat_count = cat_counts[category]

        # Go up. the hierarchy tree until you reach a good cat_count or run out of ancestors
        # The `is not None` part is not strictly needed, but here as a best practice
        while cat_count < min_queries and category is not None:
            # replace current category with its ancestor
            category = ancestors.get(category)
            # find the cat count for the new current category
            cat_count = cat_counts.get(category)
        
        return category

    # use the helper function to map the categories to their ancestors with
    # high enough counts
    return categories.map(find_ancestor_with_min_count)

if args.min_queries:
    min_queries = int(args.min_queries)

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])
# `parends_dict` has the same data as parents_df, a category->parent association
parents_dict = dict(zip(categories, parents))

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
queries_df = pd.read_csv(queries_file_name)[['category', 'query']]
queries_df = queries_df[queries_df['category'].isin(categories)]

# Map the queries with a function that normalizes text
queries_df['query'] = queries_df['query'].map(normalize_text)

# Find the categories with high enough counts
new_cats = rollup_categories(queries_df['category'], min_queries, parents_dict)
# Replace the `category` column with `new_cats`
queries_df['category'] = new_cats

# Create labels in fastText format.
queries_df['label'] = '__label__' + queries_df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
queries_df = queries_df[queries_df['category'].isin(categories)]
queries_df['output'] = queries_df['label'] + ' ' + queries_df['query']
queries_df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
