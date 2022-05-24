from fastapi import APIRouter


router = APIRouter()


@router.get("/{name}")
async def hello(name: str):
    return {"message": "Hello " + name}
