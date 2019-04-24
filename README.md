# MediaEval emotion recognition task 2019 scripts

## Requirements

* Jamendo data: `data/tracks_tags.csv`
* Warriner's list: `data/BRM-emot-submit.csv`

## Scripts

```bash
extract.py
intersect.py
plot.py 
plot.py -l -o distribution_nolables.png  # all without labels
plot.py -n 30 -o distribution_top30.png  # top30 labels
analyse.py
```
