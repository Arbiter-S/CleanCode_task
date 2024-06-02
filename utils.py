# native library imports
from datetime import datetime
from typing import List, Dict

# 3rd party library imports
from fastapi import HTTPException
from pymongo.cursor import Cursor
from bson.objectid import ObjectId
from bson.errors import InvalidId

# local imports
from database_setup import wallet_collection


class Pagination:
    DEFAULT_PAGE_SIZE = 3

    @staticmethod
    async def create_paginate_response(page, collection, match, add_wallet=False):
        """
        Returns dictionary including metadata and matched results.
        :param page: page number from url parameters
        :param collection: database collection to search
        :param match: match dictionary including the query parameters
        :param add_wallet: boolean to include wallet data
        :return: dictionary including results
        """
        page, total_docs, result = await Pagination.paginate_results(page, collection, match, add_wallet)
        return {
            "page": page,
            "pageSize": Pagination.DEFAULT_PAGE_SIZE,
            "totalPages": -(-total_docs // Pagination.DEFAULT_PAGE_SIZE) if page else 1,
            "totalDocs": total_docs if page else len(result),
            "results": result,
        }

    @staticmethod
    async def paginate_results(page, collection, match, add_wallet=False):
        """
        Handles result pagination and return results depending on the URL parameters.
        If no page is specified returns every result. If page is specified returns the specified page.
        :param page: URL parameter page number
        :param collection: database collection to use match against
        :param match: match dictionary to use for find method
        :param add_wallet: boolean to include wallet data
        :return: metadata and dictionary of results
        """
        total_docs = 0
        if page is None:
            cursor = collection.find(match)
            result = list(cursor)
            for index, doc in enumerate(result):
                # changing fields from objectId to str
                doc["_id"] = str(doc["_id"])
                if "affiliate_tracking_id" in doc:
                    doc["affiliate_tracking_id"] = str(doc["affiliate_tracking_id"])
                if "user_id" in doc:
                    doc["user_id"] = str(doc["user_id"])

                # getting the available and pending balance and adding it to document
                if add_wallet:
                    available_balance, pending_balance = await WalletManager.check_available_balance(doc["_id"])
                    doc["available_balance"] = available_balance
                    doc["pending_balance"] = pending_balance

                result[index] = await CamelCase.convert_dict_camel_case(doc)
        else:
            total_docs = collection.count_documents(match)

            if page < 1:
                page = 1

            skip = (page - 1) * Pagination.DEFAULT_PAGE_SIZE  # number of documents to skip
            limit = Pagination.DEFAULT_PAGE_SIZE

            cursor = collection.find(match)
            result = await Pagination.paginate_documents(cursor, skip, limit, add_wallet)
        return page, total_docs, result

    @staticmethod
    async def paginate_documents(cursor: Cursor, skip: int = 0, limit: int = 10, add_wallet=False) -> List[dict]:
        """
        Handles document pagination when a page is specified. Returns the documents of the given page.
        :param cursor: DB cursor pointing to the matched documents
        :param skip: number of documents to skip
        :param limit: number of documents to return
        :param add_wallet: boolean to include wallet data
        :return: a list of matched and paginated documents
        """
        cursor.skip(skip).limit(limit)
        result = list(cursor)
        for index, doc in enumerate(result):
            # changing fields from objectId to str
            doc["_id"] = str(doc["_id"])
            if "affiliate_tracking_id" in doc:
                doc["affiliate_tracking_id"] = str(doc["affiliate_tracking_id"])
            if "user_id" in doc:
                doc["user_id"] = str(doc["user_id"])

            doc = await CamelCase.convert_dict_camel_case(doc)

            # getting the available and pending balance and adding it to document
            if add_wallet:
                available_balance, pending_balance = await WalletManager.check_available_balance(doc["_id"])
                doc["availableBalance"] = available_balance
                doc["pendingBalance"] = pending_balance

            result[index] = doc
        return result


class WalletManager:

    @staticmethod
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


class CamelCase:
    @staticmethod
    async def convert_dict_camel_case(data: Dict) -> Dict:
        """
        Converts a dictionary's keys from snake case to camel case.
        :param data: dictionary to convert
        :return: dictionary with camel case keys
        """
        camel_dict = {}
        for key, value in data.items():
            camel_key = await CamelCase.snake_to_camel(key)
            camel_dict[camel_key] = value
        return camel_dict

    @staticmethod
    async def snake_to_camel(snake_str: str) -> str:
        """
        Converts a string from snake case to camel case
        :param snake_str: string to be converted.
        :return: camel case string
        """
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])


async def get_status_list_from_parameters(statuses) -> List[str]:
    """
    Returns a list of statuses from URL parameters
    :param statuses:
    :return: a list of statuses
    """
    status_list = statuses.split(",")
    lst = []
    for status in status_list:
        lst.append(status.strip())
    return lst


async def check_is_valid_objectId(identifier):
    """
    Checks for validity of an object id. Raises an exception if id is not valid.
    :param identifier:
    :return: ObjectId
    """
    try:
        return ObjectId(identifier)
    except (InvalidId, TypeError):
        raise HTTPException(detail="not valid object id", status_code=400)
