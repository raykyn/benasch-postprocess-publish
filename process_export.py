"""
This is a helper script working with postprocess.py.
Important: 
We will skip any files which do not contain at least one <Span>-Node!
"""

import glob
import postprocess
import os

# SET PATH TO RELEVANT CORPUS FOLDER
DATA = "./data/example_hgb/"

# FOLDER PATHS (best to keep like this)
UNZIPPED = os.path.join(DATA, "unzipped")
OUTPUT = os.path.join(DATA, "processed")
postprocess.OUTFOLDER = OUTPUT


if __name__ == "__main__":
    for infile in sorted(glob.glob(os.path.join(UNZIPPED, "*"))):
        postprocess.process_xmi(infile)