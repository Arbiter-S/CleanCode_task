DEFAULT_PAGE_SIZE = 3
import datetime
from typing import List
from fastapi import HTTPException
from pymongo.cursor import Cursor
from bson.objectid import ObjectId
from d_2 import wallet_collection

async def check_is_valid_objectId(id):
    try:
        return ObjectId(id)
    except:
        raise HTTPException(detail="not valid object id", status_code=400)

async def create_paginate_response(page, collection, match, add_wallet=False):
    page, total_docs, result = await paginate_results(
        page, collection, match, add_wallet
    )
    return {
        "page": page,
        "pageSize": DEFAULT_PAGE_SIZE,
        "totalPages": -(-total_docs // DEFAULT_PAGE_SIZE) if page else 1,
        "totalDocs": total_docs if page else len(result),
        "results": result,
    }

async def paginate_results(page, collection, match, add_wallet=False):
    total_docs = 0
    if page is None:
        cursor = collection.find(match)
        result = list(cursor)
        for index, doc in enumerate(result):
            doc["_id"] = str(doc["_id"])
            if "affiliate_tracking_id" in doc:
                doc["affiliate_tracking_id"] = str(
                    doc["affiliate_tracking_id"])
            if "user_id" in doc:
                doc["user_id"] = str(doc["user_id"])

            # doc = await convert_messages_id_str(doc)

            if add_wallet:
                available_balance, pending_balance = await check_available_balance(
                    doc["_id"]
                )
                doc["available_balance"] = available_balance
                doc["pending_balance"] = pending_balance

            result[index] = await convert_dict_camel_case(doc)
    else:
        total_docs = collection.count_documents(match)
        if page < 1:
            page = 1

        skip = (page - 1) * DEFAULT_PAGE_SIZE
        limit = DEFAULT_PAGE_SIZE

        cursor = collection.find(match)
        result = await paginate_documents(cursor, skip, limit, add_wallet)
    return page, total_docs, result


async def check_available_balance(user_id):
    user_id = await check_is_valid_objectId(user_id)

    wallet = wallet_collection.find_one({"user_id": user_id})

    # Calculate the available and pending balance
    available_balance = wallet['available_balance']
    pending_balance = 0
    transactions_to_delete = []
    for transaction in wallet["transactions"]:
        if transaction["date_available"] <= datetime.now():
            available_balance += transaction["amount"]
            transactions_to_delete.append(transaction["id"])
        else:
            pending_balance += transaction["amount"]

    # Update the wallet with the new balances
    wallet_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "available_balance": available_balance,
                "pending_balance": pending_balance,
            },
            "$pull": {
                "transactions": {"id": {"$in": transactions_to_delete}}
            },
        },
    )
    return available_balance, pending_balance




async def snake_to_camel(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])



async def convert_dict_camel_case(data):
    camel_dict = {}
    for key, value in data.items():
        camel_key = await snake_to_camel(key)
        camel_dict[camel_key] = value
    return camel_dict


async def paginate_documents(
    cursor: Cursor, skip: int = 0, limit: int = 10, add_wallet=False
) -> List[dict]:
    cursor.skip(skip).limit(limit)
    result = [doc for doc in cursor]
    for index, doc in enumerate(result):
        _id = doc["_id"]
        doc["_id"] = str(doc["_id"])
        if "affiliate_tracking_id" in doc:
            doc["affiliate_tracking_id"] = str(doc["affiliate_tracking_id"])
        if "user_id" in doc:
            doc["user_id"] = str(doc["user_id"])

        # doc = await convert_messages_id_str(doc)
        doc = await convert_dict_camel_case(doc)
        if add_wallet:
            print(add_wallet)
            available_balance, pending_balance = await check_available_balance(_id)
            doc["availableBalance"] = available_balance
            doc["pendingBalance"] = pending_balance
            # print(doc)
        result[index] = doc
    return result