# native library imports
from typing import Optional, Dict, Any
from datetime import datetime

# 3rd party library imports
from fastapi import FastAPI, Depends
import uvicorn

# local imports
from authentication import Authentication
from database_setup import payout_collection
from utils import Pagination, get_status_list_from_parameters

app = FastAPI()

authentication_manager = Authentication()


@app.get("/payout")
async def all_payout(
        statuses: Optional[str] = None,
        page: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_type: Optional[str] = None,
        payment_start_date: Optional[datetime] = None,
        payment_end_date: Optional[datetime] = None,
        admin: str = Depends(authentication_manager.check_user_is_admin),
) -> Dict[str, Any]:
    """
    Returns a filtered list of payouts based on URL parameters

    :param statuses: Comma seperated statuses to use in filtering
    :param page: Page number to use for pagination
    :param start_date: Date to use as the starting date for "created" field
    :param end_date: Date to use as the ending date for "created" field
    :param user_type: Type of user to use in filtering
    :param payment_start_date: Date to use as the starting date for "payment_date" field
    :param payment_end_date:Date to use as the ending date for "payment_date" field
    :param admin: checks whether the user is admin. Raises exception if not
    :return: Dictionary including metadata and list of filtered payouts
    """
    match = {}

    # filters for creation date
    if start_date or end_date:
        match['created'] = {}
        if start_date:
            match['created']['$gte'] = start_date
        if end_date:
            match['created']['$lte'] = end_date

    # filters for payment date
    if payment_start_date or payment_end_date:
        match['payment_date'] = {}
        if payment_start_date:
            match['payment_date']['$gte'] = payment_start_date
        if payment_end_date:
            match['payment_date']['$lte'] = payment_end_date

    # filters for user type
    if user_type:
        match['user_type'] = user_type
    # filters for status
    if statuses:
        status_list = await get_status_list_from_parameters(statuses)
        match['status'] = {'$in': status_list}

    return await Pagination.create_paginate_response(page, payout_collection, match)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
