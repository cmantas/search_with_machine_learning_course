import argparse
import multiprocessing
import glob
from tqdm import tqdm
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from itertools import chain
from collections import defaultdict, Counter

def transform_name(product_name):
    # IMPLEMENT
    return product_name

# Directory for product data
directory = r'/workspace/datasets/product_data/products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")
general.add_argument("--label", default="id", help="id is default and needed for downsteam use, but name is helpful for debugging")
general.add_argument("--limit-files", default=None, type=int)

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input
# IMPLEMENT: Track the number of items in each category and only output if above the min
min_products = args.min_products
names_as_labels = False
if args.label == 'name':
    names_as_labels = True

def _label_filename(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    labels = []
    for child in root:
        # Check to make sure category name is valid and not in music or movies
        if (child.find('name') is not None and child.find('name').text is not None and
            child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
            child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None and
            child.find('categoryPath')[0][0].text == 'cat00000' and
            child.find('categoryPath')[1][0].text != 'abcat0600000'):
              # Choose last element in categoryPath as the leaf categoryId or name
              if names_as_labels:
                  cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][1].text.replace(' ', '_')
              else:
                  cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
              # Replace newline chars with spaces so fastText doesn't complain
              name = child.find('name').text.replace('\n', ' ')
              labels.append((cat, transform_name(name)))
    return labels

def remove_low_freq_categories(data, min_count=1):
    # create a category counts dict from all data
    cat_counts = defaultdict(int)
    for cat, _ in data:
        cat_counts[cat] += 1
    # keep elements whose categories that have counts > min_count
    return filter(lambda t: cat_counts[t[0]]>=min_count, data)


if __name__ == '__main__':
    files = glob.glob(f'{directory}/*.xml')
    #Limit files to process (for testing purposes)
    if args.limit_files:
        files = files[:args.limit_files]

    print("Writing results to %s" % output_file)
    with multiprocessing.Pool() as p:
        # read data from each xml to a list using a pool of workers 
        # (creates an iterable of lists of label-text pairs)
        all_labels = tqdm(p.imap(_label_filename, files), total=len(files))
        # flatten data from all files (creates a list of label-text pairs)
        data_lines = list(chain(*all_labels))
        # remove low frequency cateogories
        data_lines = remove_low_freq_categories(data_lines, min_products)
        # write to output file
        with open(output_file, 'w') as output:
            for (cat, name) in data_lines:
                output.write(f'__label__{cat} {name}\n')
