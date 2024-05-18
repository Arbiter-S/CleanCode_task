from typing import Optional
from fastapi import FastAPI, Depends
from datetime import datetime
from d_1 import *
from d_2 import *

router = FastAPI()

from tools import create_paginate_response
@router.get("/payout")
async def all_payout(
    statuses: Optional[str] = None, page: Optional[int] = None, start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None, user_type: Optional[str] = None,
    payment_start_date:  Optional[datetime] = None, payment_end_date: Optional[datetime] = None,
    admin: str = Depends(check_user_is_admin)
):
    match = {'created':  {}, "payment_date": {}}

    if start_date:
        match['created']['$gte'] = start_date
    if end_date:
        match['created']['$lte'] = end_date

    if payment_start_date:
        match['payment_date']['$gte'] = payment_start_date
    if payment_end_date:
        match['payment_date']['$lte'] = payment_end_date
    if len(match['created']) == 0:
        del match["created"]
    if len(match["payment_date"]) == 0:
        del match["payment_date"]
    if user_type:
        match['user_type'] = user_type
    if statuses:
        status_list = await get_status_list_from_query(statuses)
        match['status'] = {'$in': status_list}

    return await create_paginate_response(page, payout_collection, match)