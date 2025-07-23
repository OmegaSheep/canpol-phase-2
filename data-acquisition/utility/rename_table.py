"""We don't create slugs in the individual data scripts, especially older ones - so this can be used to add them later."""

import pymongo
from slugify import slugify
import sys
sys.stdout.reconfigure(encoding='utf-8')

env = open('../../.env')
mongo_uri=''
for line in env:
    if line.startswith('MONGO_URI'):
        mongo_uri = line.split('MONGO_URI=')[1].replace("'", "")

myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["public_gov"]

# Rename the collection from 'mps_copy' to 'federal_mps'
def rename_collection(db, old_name, new_name):
    if old_name in db.list_collection_names():
        db[old_name].rename(new_name)
        print(f"Renamed collection '{old_name}' to '{new_name}'")
    else:
        print(f"Collection '{old_name}' does not exist.")

rename_collection(mydb, "mps_copy", "federal_mps")