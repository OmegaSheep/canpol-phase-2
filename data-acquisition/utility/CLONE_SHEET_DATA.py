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

reps = mydb["mps_copy"] # Change to relevant table.
sheet_data = mydb["sheet_data"] # Change to relevant table.
mps_status = mydb["mps_status"] # Change to relevant table.

for i in reps.find({}):
    sheet = sheet_data.find_one({ 'name': i['name'] })

    if sheet:
        mps_status.insert_one({
            'name': i['name'],
            'landlord': sheet['landlord'],
            'investor': sheet['investor'],
        })
    else:
        mps_status.insert_one({
            'name': i['name'],
            'landlord': "UNDISCLOSED",
            'investor': "UNDISCLOSED",
        })