import fasttext, csv

# a threshold for the max distance the neighbors can have
similarity_threshold = .75
k = 25 # setting k to a large value so as to only rely on "threshold"

model_fname = '/workspace/datasets/fasttext/norm_title_model_20.bin'
top_words_fname = '/workspace/datasets/fasttext/top_words.txt'
csv_output_fname = '/workspace/datasets/fasttext/synonyms.csv'

# Load the FT model
model = fasttext.load_model(model_fname)

# load the top_words
with open(top_words_fname) as f:
    top_words = [l.strip() for l in f]

# create a helper function for producing neihgbor words ("synonyms")
def get_nn_words(word):
    pairs = model.get_nearest_neighbors(word, k=k)
    return [
        word 
        for dist, word in pairs 
        if dist>=similarity_threshold
    ]


def create_neighbor_pairs(words):
    """Given a list of words, it uses `get_nn_words` to get its neighbors (synonyms) 
    and for each neighbor it yields a pair of (word, neighbor_word)
    """
    for w in words:
        for neighbor in get_nn_words(w):
            yield w, neighbor

# a generator for word, neighbor pairs
neighbor_gen = create_neighbor_pairs(top_words)


counter = 0
# write to the csv file
with open(csv_output_fname, 'w') as f:
    writer = csv.writer(f)
    # iterate all pairs and write to csv
    for word, neighbor in neighbor_gen:
        writer.writerow((word, neighbor))
        counter += 1

print("wrote", counter, "pairs")