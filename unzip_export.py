"""
Executing this script will unzip the exported documents.
"""

import glob
import os
import zipfile


# SET PATH TO RELEVANT CORPUS FOLDER
DATA = "./data/example_hgb/"

# FOLDER PATHS (best to keep like this)
EXPORT = os.path.join(DATA, "exports")
UNZIPPED = os.path.join(DATA, "unzipped")

# Which annotators to process, leave empty for all
ANNOTATORS = []


if __name__ == "__main__":
    for infolder in glob.glob(os.path.join(EXPORT, "*")):
        if not os.path.isdir(infolder):  # don't process the zip files
            continue

        annotation_folder = os.path.join(infolder, "annotation")

        filefolders = sorted(glob.glob(os.path.join(annotation_folder, "*")))

        for filefolder in filefolders:
            userfolders = sorted(glob.glob(os.path.join(filefolder, "*.zip")))

            for userfolder in userfolders:
                username = os.path.basename(userfolder).replace(".zip", "")
                if username == "INITIAL_CAS":
                    continue
                if ANNOTATORS and username not in ANNOTATORS:
                    continue
                archive = zipfile.ZipFile(userfolder, 'r')
                xmi = archive.read(username + ".xmi")

                # write the xmi to the unzipped folder
                if not os.path.exists(UNZIPPED):
                    os.makedirs(UNZIPPED)
                with open(os.path.join(UNZIPPED, username + "_" + os.path.basename(filefolder)).replace(".txt", ".xmi"), 'wb') as f:
                    f.write(xmi)