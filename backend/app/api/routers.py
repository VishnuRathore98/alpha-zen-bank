from fastapi import APIRouter

router = APIRouter()


@router.get()
def home():
    return {
        "message": "welcome to the alpha zen bank, where security and technology shake hands"
    }
