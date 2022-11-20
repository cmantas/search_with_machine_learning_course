# Week 3 Assessment

## Level 1: Query Classification

### a. How many unique categories did you see in your rolled up training data when you set the minimum number of queries per category to 1000? To 10000?

For 1K: 477, for 1K: 100:

### b. What were the best values you achieved for R@1, R@3, and R@5? You should have tried at least a few different models, varying the minimum number of queries per category, as well as trying different fastText parameters or query normalization. Report at least 2 of your runs.

For default arguments, trained on the 50K dateset and tested on the 10K
```
P@1, R@1:     0.464
P@5     0.136
R@5     0.682
```

Using 20 epochs, a learning rate of 0.75 and 2 word-N-grams (same datasets)
```
P@1, R@1: 0.509
P@5     0.152
R@5     0.762
```

The quries were just lowercased, not stemmed (due to a lack of time, but I think that's better anyway for this dataset)

## Level 2: Integrade query classfication with Search

### a. Give 2 or 3 examples of queries where you saw a dramatic positive change in the results because of filtering. Make sure to include the classifier output for those queries.

Lets examine the `iphone` and `galaxy` queries. The output of the `query.py` script was modified to include the 
classifier output (eg `Categ: something1345 Conf: 0.99`), the total hits, and only the name of the SKU.

Note: the count in the "boosting" cases is slightly increased because of the query logic. It was simpler to 
just add the new (boosting) clauses to the existing `should` array, but this slightly
relaxed the its filtering. This actually affects the results decreasing the precision a bit.

#### `iphone`: default

```
Total Hits:  3201 

ZAGG - InvisibleSHIELD HD for Apple® iPhone® 4 and 4S
LifeProof - Case for Apple® iPhone® 4 and 4S - Black
ZAGG - InvisibleSHIELD for Apple® iPhone® 4 - Clear
LifeProof - Case for Apple® iPhone® 4 and 4S - White
Rocketfish™ Mobile - Mini Stereo Cable for Apple® iPhone
Apple® - iPhone 4 with 8GB Memory - White (AT&T)
Rocketfish™ - Premium Vehicle Charger for Apple® iPad™, iPhone® and iPod®
ZAGG - Smudge Free Shield for Apple® iPhone® 4 and 4S
LifeProof - Case for Apple® iPhone® 4 and 4S - Pink
LifeProof - Case for Apple® iPhone® 4 and 4S - Purple
```
As we can see, the 1st smarthphone of this query appears on the 6th slot. not particularly good

#### `iphone`: category boosting
```
Categ: pcmcat209000050008 Conf: 0.69

Total Hits:  3616 

Apple® - iPhone 4 with 8GB Memory - White (AT&T)
Apple® - iPhone 4 with 8GB Memory - White (Verizon Wireless)
Apple® - iPhone 4 with 8GB Memory - Black (AT&T)
Apple® - iPhone® 4S with 16GB Memory Mobile Phone - White (AT&T)
Apple® - iPhone 4 with 8GB Memory - Black (Verizon Wireless)
Apple® - iPhone 4 with 8GB Memory - White (Sprint)
Apple® - iPhone® 4S with 16GB Memory Mobile Phone - Black (AT&T)
Apple® - iPhone® 4S with 16GB Memory Mobile Phone - White (Verizon Wireless)
ZAGG - InvisibleSHIELD HD for Apple® iPhone® 4 and 4S
LifeProof - Case for Apple® iPhone® 4 and 4S - Black
```

Much better. All but the last 2 of the top-10 are iphone smartphones.  


#### `iphone`: category filtering
```
Categ: pcmcat209000050008 Conf: 0.69

Total Hits:  63 

Apple® - iPhone 4 with 8GB Memory - White (AT&T)
Apple® - iPhone 4 with 8GB Memory - White (Verizon Wireless)
Apple® - iPhone 4 with 8GB Memory - Black (AT&T)
Apple® - iPhone 4 with 8GB Memory - White (Sprint)
Apple® - iPhone 4 with 8GB Memory - Black (Verizon Wireless)
Apple® - iPhone® 4S with 16GB Memory Mobile Phone - White (AT&T)
Apple® - iPhone® 4S with 16GB Memory Mobile Phone - Black (AT&T)
Apple® - iPhone® 4S with 16GB Memory Mobile Phone - White (Verizon Wireless)
Apple® - iPhone® 4 with 8GB Memory - Black (Sprint)
Apple® - iPhone® 4S with 16GB Memory Mobile Phone - Black (Verizon Wireless)
```
Same picture as before, just only limited to 1 category

#### `galaxy`: default
```
Total Hits:  741 

ZAGG - InvisibleSHIELD HD for Samsung Galaxy S III Mobile Phones
Samsung - Galaxy Tab 2 7.0 with 8GB Memory - Titanium Silver
ZAGG - InvisibleSHIELD for Samsung Galaxy S III Mobile Phones
Samsung - Galaxy S III 4G Mobile Phone - Marble White (Sprint)
Samsung - Galaxy Tab 2 10.1 with 16GB Memory - Titanium Silver
Samsung - Galaxy S II Epic 4G Touch Mobile Phone - White (Sprint)
Samsung - Galaxy S III 4G Mobile Phone - Pebble Blue (Sprint)
Samsung - Galaxy S III 4G Mobile Phone - Marble White (AT&T)
Samsung - Galaxy S II Epic 4G Touch Mobile Phone - Black (Sprint)
Rocketfish™ - Snap-On Case for Samsung Galaxy S III Mobile Phones - Gray
```

The 1st and 3rd places are not actual galaxy products.
**Note:** it seems that bestbuy had both tablets and smartphones in the same category at a the time,
so seeking `Galaxy Tab` in the results actually makes sense.


#### `galaxy`: category boosting
```
Categ: pcmcat209000050008 Conf: 0.69

Total Hits:  899 

Samsung - Galaxy Tab 2 7.0 with 8GB Memory - Titanium Silver
Samsung - Galaxy Tab 2 10.1 with 16GB Memory - Titanium Silver
ZAGG - InvisibleSHIELD HD for Samsung Galaxy S III Mobile Phones
ZAGG - InvisibleSHIELD for Samsung Galaxy S III Mobile Phones
Samsung - Galaxy S III 4G Mobile Phone - Marble White (Sprint)
Samsung - Galaxy S II Epic 4G Touch Mobile Phone - White (Sprint)
Samsung - Galaxy S III 4G Mobile Phone - Pebble Blue (Sprint)
Samsung - Galaxy S III 4G Mobile Phone - Marble White (AT&T)
Samsung - Galaxy S II Epic 4G Touch Mobile Phone - Black (Sprint)
Rocketfish™ - Snap-On Case for Samsung Galaxy S III Mobile Phones - Gray
```

We fixed the top 2 cases, but we still have accessories in positions 3,4,10.
This is better.


#### `galaxy`: category fitering
```
Categ: pcmcat209000050008 Conf: 0.69


Total Hits:  23 

Samsung - Galaxy Tab 2 7.0 with 8GB Memory - Titanium Silver
Samsung - Galaxy Tab 2 10.1 with 16GB Memory - Titanium Silver
Samsung - Galaxy Tab 3G (Verizon Wireless)
Samsung - Galaxy Tab 10.1 - 16GB - White
Samsung - Galaxy Tab 10.1 - 32GB - White
Samsung - Galaxy Tab with 16GB Memory - Chic White
Samsung - Galaxy Tab 10.1 - 16GB - Metallic Gray
Samsung - Galaxy Tab 10.1  - 32GB - Metallic Gray
Samsung - Galaxy Tab 3G with 16GB Storage Memory
Samsung - Refurbished Galaxy Tablet with 16GB Memory - Metallic Gray
```

As expected this returns only results in smartphones/tablets.


### b. Give 2 or 3 examples of queries where filtering hurt the results, either because the classifier was wrong or for some other reason. Again, include the classifier output for those queries.

`iphone case` and `galaxy case` both return zero results for some reason when filtering with categories.
I'm not sure why that is, and don't actually have the time to debug it.

For `iphone` the clasffier had these results categories as results  

* "iPhone Accessories/Cases"  with 0.47 (`pcmcat214700050000`)
* "Mobile Phone Cases & Clips/Fitted" with 0.4 (`pcmcat171900050029`)

For `galaxy`:

* "Mobile Phone Cases & Clips/Fitted" with  0.69 (`pcmcat171900050029`)
* "Tablet Accessories/Tablet Cases, Covers & Sleeves" with 0.29 (`pcmcat242000050002`)

These classification results seem to actually be correct, so I should either have an error in the query logic,
(or there could be some data missing in the index). It could also be some kind of stemming error, because 
`galaxy cases` actually returns results. 

This is indicative of the fact that when using a "hard" filtering approach, you can shoot yourself in the foot
and degrade the user experience. A logical workaround approach to such problems could be to fallback to the non-filtered results when getting zero results from the filtered ones.