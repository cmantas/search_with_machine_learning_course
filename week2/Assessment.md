# L1: Classifying product names to categories:

## 1.a What precision (P@1) were you able to achieve?
```
P@1     0.971
R@1     0.971
P@5     0.2
R@5     0.999
```

## 1.b What fastText parameters did you use?
 `-lr 1 -wordNgrams 2`  
 Used a pruned, normalized dataset

## 1.c How did you transform the product names?

Did not do anything other than the instructions:
```
cat /workspace/datasets/fasttext/pruned_shuffled_labeled_products.txt | \
   sed -e "s/\([.\!?,'/()]\)/ \1 /g" | \
   tr "[:upper:]" "[:lower:]" | \
   sed "s/[^[:alnum:]_]/ /g" | \
   tr -s ' ' > \
   /workspace/datasets/fasttext/pruned_shuffled_shuffled_labeled_products.txt
```

## 1.d How did you prune infrequent category labels, and how did that affect your precision?
I chose to materialize the whole dataset (`all_labels`) in-memory, then pass it to a new
function `remove_low_freq_categories` that counted label occurences and removed the low-frequency ones.  
Precision increased dramatically. Original results (before pruning) were:
```
P@1     0.215
R@1     0.215
P@5     0.0809
R@5     0.404
```

## 1.e How did you prune the category tree, and how did that affect your precision?

I did not prune it. It seems like an excellent idea, much better than prunning. 
I'll keep it in mind for future use.

# L2: Deriving synonyms from content

## 2.a What were the results for your best model in the tokens used for evaluation?
Here's the output. of a showcase script I made for that `(.89)` next to a word means it had `0.89` fasttext score.  
The threshold is `0.75` that's why some words don't have any neighbors.

The script is called `week2/create_synonyms.py` and it's the same for creating the elasticsearch config file.

```
Word: laptop
Neighbors:
 =[nothing]= 

Word: freezer
Neighbors:
 refrigerator (.81) | refrigerators (.76) | frost (.75) 

Word: nintendo
Neighbors:
 ds (.9) | wii (.89) | 3ds (.84) | rabbids (.78) | gamecube (.76) 

Word: whirlpool
Neighbors:
 biscuit (.83) | maytag (.83) | frigidaire (.79) | bisque (.77) 

Word: kodak
Neighbors:
 easyshare (.84) | m1063 (.77) | m863 (.77) 

Word: ps2
Neighbors:
 ps3 (.85) | gba (.8) | guide (.78) | nhl (.75) 

Word: razr
Neighbors:
 8530 (.85) | sgh (.84) | 8520 (.83) | motorola (.82) | sph (.81) | droid (.78) | jabra (.78) | nokia (.77) | kyocera (.77) | scuba (.76) | 9700 (.76) | atrix (.76) | cellsuit (.76) | communications (.76) | phones (.75) 

Word: stratocaster
Neighbors:
 telecaster (.92) | strat (.84) | squier (.81) | sunburst (.77) | fretboard (.76) | fender (.76) 

Word: holiday
Neighbors:
 hanukkah (.8) | kwanzaa (.8) | cumpleaños (.79) | navidad (.78) | gift (.77) | joy (.77) | gc (.76) | thank (.76) | feliz (.76) | happy (.76) | birthday (.75) 

Word: plasma
Neighbors:
 600hz (.85) | hdtvs (.78) | 63 (.78) | 58 (.78) | viera (.76) | 240hz (.75) 

Word: leather
Neighbors:
 =[nothing]=
```


## 2.b What fastText parameters did you use?
```
For training:
~/fastText-0.9.2/fasttext skipgram \
    -input /workspace/datasets/fasttext/normalized_titles.txt \
    -output /workspace/datasets/fasttext/norm_title_model_20 \
    -minCount 20
```
For synonyms generation, I used a threshold of `.75`

## 2.c How did you transform the product names?
I used the same bash command as before
```
cat /workspace/datasets/fasttext/titles.txt | \
sed -e "s/\([.\!?,'/()]\)/ \1 /g" | \
tr "[:upper:]" "[:lower:]" | \
sed "s/[^[:alnum:]]/ /g" | tr -s ' ' \
> /workspace/datasets/fasttext/normalized_titles.txt
```

# L3: integrating synonyms with search:

## 3.a How did you transform the product names (if different than previously)?

Same as before.

## 3.b What threshold score did you use?
This was handled by the `create_synonyms.py` script. The threshold is `.75`

# 3.c Were you able to find the additional results by matching synonyms?
With the exception of `nespresso` which was not in my `top_words.txt` for some reason, yes!
```
earbuds 1205 vs 3139
nespresso 8 vs 8 (?) <- not in top words
dslr 2837 vs 6592
```

# L4: Classifying reviews:

## 4.a What precision (P@1) were you able to achieve?
-

## 4.b What fastText parameters did you use?
-

## 4.c How did you transform the review content?
-

## 4.d What else did you try and learn?
-