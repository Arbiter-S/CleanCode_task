import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

MONGO_INITDB_DATABASE = os.getenv('MONGO_INITDB_DATABASE')
MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_HOST = os.getenv('MONGO_HOST')

remote_db = "mongodb+srv://alisarbakhshi08:qw5CSiATJiMph96g@cluster0.fztkmxw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_HOST}", port=27017)


db = client[MONGO_INITDB_DATABASE]
user_collection = db['users_affiliate3']
wallet_collection = db['users_wallet']
payout_collection = db['payout_affiliate']
