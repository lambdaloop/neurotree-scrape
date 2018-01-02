# Neurotree scraping 

This is the code for scraping neurotree to get faculty placement rates.

In order to reproduce my results, run:
```bash
cp neuroscience.csv.orig neuroscience.csv
python3 scrape_neurotree.py
python3 find_placement_stats.py
```

The above will produce a table of placement rates for PhDs from the institution. 
In order to get the rates for post-docs, uncomment the line below in `find_placement_stats.py` and run that file again:
```python
phd = person['post-doc'] # for post-doc rates
```



