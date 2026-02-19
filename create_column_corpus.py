"""
Use this script to generate IOB-formatted training data.
The input files are the BeNASch formatted files.

This script will also handle the resolution of a file that was annotated by more than 1 user.
We handle it with the following solution:
Ranking: Requires additionally a list of the user names and will take the first-named users file over latter named users files.

This script can also automatically split your data into training, validation and test sets. 
Please use the script TODO in the utility folder to generate a split file that will record your splits for further use.
If you prefer your data not to be split, simply leave the path to the split file empty.
"""


import json
import os
from glob import glob
import pathlib
from transformation.to_column import process_document


### SETTINGS ###
DATA = "./data/gewerbuecher_2026_02_18/"
INFOLDER = os.path.join(DATA, "processed")
OUTFOLDER = os.path.join(DATA, "all_spans")
CONSISTENT_DATA = ""


### PROCESSING CONGIG ###
PROCESSING_CONFIG = {
    # in "base", set which annotation layers will be used for samples.
    # "." indicates the whole text
    "base": [
        {"xpath": ".", "label": "DOC"},
        {"xpath": ".//b:span[not(@element='head' or @element='value' or @element='trigger' or @element='mod')]", "label": ["@element", "@class"]},
        {"xpath": ".//b:span[@element='mod'][count(*) > 0]", "label": ["@element", "@class"]}
    ],
    # in "columns", we define which annotations are written for training
    # if multiple layers would fit the xpath, only the first one in order is used
    # multiple columns can be defined in this way
    "columns": [
        [
            # multiple xpaths can be defined with different tag conversion instructions
            # mind you, if a node fits multiple xpaths, only the first one is used
            {"xpath": ".//b:span[@element='list']", "tag": ["@element"]},
            {"xpath": ".//b:span[@element='reference'][b:span[@class='pro']]", "tag": ["pro"]},
            {"xpath": ".//b:span", "tag": ["@element", ".", "@class"]}
            #{"xpath": ".//span[@element='head']", "tag": ["@element", ".", "@class"]}
            #{"xpath": ".//b:span[@element='reference']", "tag": ["@class"]}
        ]
    ],
    # if you would like to rename specific tags for the purpose of annotation, you can set it here
    "rename_labels": {
        #"fac": "loc",
        #"gpe-org": "org",
        #"gpe-loc": "loc",
        #"gpe": "loc",
        #"other": "misc",
        #"nam": "loc"
    }
}


def main(infolder, outfolder, training_splits, config=None):
    pathlib.Path(outfolder).mkdir(parents=True, exist_ok=True) 

    infiles = sorted(glob(os.path.join(infolder, "*.xml")))

    tagset = set()

    if training_splits:
        trainfile = open(os.path.join(outfolder, "train.txt"), mode="w", encoding="utf8")
        devfile = open(os.path.join(outfolder, "dev.txt"), mode="w", encoding="utf8")
        testfile = open(os.path.join(outfolder, "test.txt"), mode="w", encoding="utf8")
        with open(training_splits, mode="r", encoding="utf8") as cons:
            consistent_data = json.load(cons)
    else:
        writer = open(os.path.join(outfolder, "columns.txt"), mode="w", encoding="utf8")
        consistent_data = None

    for infile in infiles:
        print(f"Processing {infile}...")
        outstring, tags = process_document(infile, config=config)
        tagset.update(tags)
        basename = os.path.basename(infile)
        
        if consistent_data is not None:
            if basename in consistent_data["test"]:
                writer = testfile
            elif basename in consistent_data["dev"]:
                writer = devfile
            elif basename in consistent_data["train"]:
                writer = trainfile
            else:
                print(f"WARNING! {infile} was not found in consistent training registry!")
                continue

        # write the filename as a comment (flair ignores these in ColumnCorpus)
        if outstring:
            writer.write(f"# {os.path.basename(infile)}\n")
            writer.write(outstring)
            writer.write("\n")

    if training_splits:
        trainfile.close()
        devfile.close()
        testfile.close()

    print("Tags in the dataset:", sorted(tagset))


if __name__ == "__main__":
    main(INFOLDER, OUTFOLDER, CONSISTENT_DATA, config=PROCESSING_CONFIG)
