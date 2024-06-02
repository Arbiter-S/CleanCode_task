# 3rd party library imports
import pytest
from fastapi import HTTPException

# local imports
from authentication import Authentication


@pytest.mark.asyncio
async def test_email_from_token():
    token = ('Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbkB0ZX'
             'N0LmNvbSJ9.2rKwigP6hPq-L6ssB7SSdPddf7TXSE_AIYzAhF2LMPo')
    changed_token = token[:-1]
    assert 'admin@test.com' == await Authentication.get_email_from_token(token)
    with pytest.raises(HTTPException):
        await Authentication.get_email_from_token(changed_token)


