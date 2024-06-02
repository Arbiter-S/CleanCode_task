# native library imports
import os

# 3rd party library imports
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_INITDB_DATABASE = os.getenv('MONGO_INITDB_DATABASE')
MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_HOST = os.getenv('MONGO_HOST')

test_db = ('mongodb+srv://alisarbakhshi08:qw5CSiATJiMph96g@cluster0.fztkmxw.mongodb.net/?retryWrites='
           'true&w=majority&appName=Cluster0')

client = MongoClient(test_db) if os.getenv('TEST') == 'True' else MongoClient(host=MONGO_HOST, port=27017,
                                                                              username=MONGO_INITDB_ROOT_USERNAME,
                                                                              password=MONGO_INITDB_ROOT_PASSWORD)

db = client[MONGO_INITDB_DATABASE]
user_collection = db['users_affiliate3']
wallet_collection = db['users_wallet']
payout_collection = db['payout_affiliate']
