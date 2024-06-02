# 3rd party library imports
import pytest
from fastapi import HTTPException
from bson import ObjectId

# local imports
from utils import check_is_valid_objectId, get_status_list_from_parameters, CamelCase


@pytest.mark.asyncio
async def test_invalid_objectId():
    with pytest.raises(HTTPException):
        await check_is_valid_objectId("foo")

    assert ObjectId('66486ee1b86db43ec2084533') == await check_is_valid_objectId('66486ee1b86db43ec2084533')


@pytest.mark.asyncio
async def test_status_parameters():
    result = await get_status_list_from_parameters("done,pending,canceled")
    assert result == ["done", "pending", "canceled"]


@pytest.mark.asyncio
async def test_camel_case():
    doc = {'some_key': 'some_value', 'random_key': 'random_value'}
    result = await CamelCase.convert_dict_camel_case(doc)
    assert result == {'randomKey': 'random_value', 'someKey': 'some_value'}
