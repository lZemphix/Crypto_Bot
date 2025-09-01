from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/logout", tags=["auth"])
async def logout():
    # For HTTP Basic Auth, the only way to "log out" is to send a 401 Unauthorized
    # response. This tells the browser to clear its credentials for the site
    # and re-prompt the user on the next visit.
    raise HTTPException(
        status_code=401,
        detail="Logged out",
        headers={"WWW-Authenticate": "Basic"},
    )
