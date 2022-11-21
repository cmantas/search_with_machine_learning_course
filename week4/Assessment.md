## Querying

here is the output of some queries with "regular" vs vector search

"iphone" (regular)
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

"iphone" (vector)
```
Total Hits:  113 

Incase - Case for Apple® iPhone
Incase - Hybrid Cover for Apple® iPhone® 4 - Black
Incase - Sport Case for Apple® iPhone - Black
Apple® - The new iPad® with Wi-Fi + Cellular - 32GB (Verizon) - White
Apple® - The new iPad® with Wi-Fi + Cellular - 32GB (Verizon) - Black
Apple® - The new iPad® with Wi-Fi + Cellular - 16GB (AT&T) - White
Apple® - The new iPad® with Wi-Fi + Cellular  - 16GB (Verizon) - White
Apple® - The new iPad® with Wi-Fi + Cellular - 16GB (Verizon) - Black
Apple® - The new iPad® with Wi-Fi + Cellular - 32GB (AT&T) - White
Apple® - The new iPad® with Wi-Fi + Cellular - 64GB (Verizon) - White
```

^ this was done with zero tuning. I don't know the threshold for the cosine used for
achieving the tota hits of 113...  
Anyway it's clear that the results are more "semantic", since the actual word "iphone"
is missing from some of them, but they're also conceputally relevant (eg. Ipad).
(Note: phones and tablets seem to be on the same bestbuy category)

"galaxy" (regular)
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

"galaxy" (vector)
```
Galaxy of Games 3001 - Windows
Galaxy of Games - Windows
Galaxy of Sports - Windows
Galaxy of Games 1500 - Windows
Galaxy of Games 10,000 - Windows
3M - Precise Mousing Surface - Star Galaxy
Galaxy of MahJongg 1,000,000 - Windows
Galaxy of Board Games - Windows
Galaxy Racers - Nintendo DS
Galaxy of Games 50,000 - Window
```

That's arguably terrible results. There is also nothing "semantic" about them...   
This can serve as a testament to two things
* The fact that the model was trained in non-ecommerce dat
* the usefulness of "offline" features (query-independent) features


"samsung galaxy" (regular)
```
Total Hits:  3070 

ZAGG - InvisibleSHIELD HD for Samsung Galaxy S III Mobile Phones
ZAGG - InvisibleSHIELD for Samsung Galaxy S III Mobile Phones
Rocketfish™ - Snap-On Case for Samsung Galaxy S III Mobile Phones - Gray
OtterBox - Commuter Series Case for Samsung Galaxy S III Mobile Phones - Black
Platinum Series - Case with Holster for Samsung Galaxy S III Mobile Phones - Black
Boost Mobile - Samsung Galaxy Prevail No-Contract Mobile Phone - Black
Belkin - Bifold Folio Case for Samsung Galaxy Tab 2 7.0
Samsung - Galaxy Tab 2 7.0 with 8GB Memory - Titanium Silver
ZAGG - InvisibleSHIELD for Samsung Galaxy Tab 2 7.0
Samsung - Galaxy Tab 2 10.1 with 16GB Memory - Titanium Silver
```

"samsung galaxy" (vector)
```
Total Hits:  113 

Samsung - Ultra Mobile PC
Samsung - Galaxy S III 4G Mobile Phone (Unlocked) - White
Samsung - Galaxy S III 4G Mobile Phone (Unlocked) - White
Samsung - Galaxy Fit S5670 Mobile Phone (Unlocked) - Black/Silver
Samsung - Galaxy Fit S5670 Mobile Phone (Unlocked) - Black/Silver
Samsung - Galaxy Tab 10.1 - 16GB - White
Samsung - Galaxy S III 4G Mobile Phone - Marble White (AT&T)
Samsung Galaxy Tab 2 7.0 Tablet, Stylus and Screen Protector Package
Samsung - Slate Tablet - Black
Samsung - Galaxy Ace Mobile Phone (Unlocked) - Black
```

Ok this is somewhat better. Adding another word to the query seems to be adding
a lot of more semantic informantion. It seems to now know we're talking about a 
smartphone.  
Good.

## Filtering
"galaxy" (vector + filtering)
```
Total Hits:  2 

Samsung - Galaxy Tab 10.1 - 16GB - White
Samsung Galaxy Tab 2 7.0 Tablet, Stylus and Screen Protector Package
```
OK this is much improved!! Why just 2 hits though?  
We should give our KNN the chance to retreive more docs.  Let's change the logic
 to update K by a factor of 10:

 ```
 Total Hits:  29 

Samsung - Galaxy Tab 10.1 - 16GB - White
Samsung - Galaxy Tab 3G (Verizon Wireless)
Samsung - Galaxy Tab with 16GB Memory - Chic White
Samsung - Galaxy Tab 10.1 - 32GB - White
Samsung - Galaxy Tab 10.1 with 16GB Memory - Metallic Gray
Samsung Galaxy Tab 2 7.0 Tablet, Stylus and Screen Protector Package
Samsung - Galaxy Tab 10.1 with 32GB Memory - Metallic Gray
Samsung - Galaxy Tab 7.0 Plus with 16GB Memory - Metallic Gray
Samsung - Galaxy Tab 10.1 with 16GB Memory (Verizon) - Metallic Gray
Samsung - Slate Tablet - Black
 ```

This is greately improved!
