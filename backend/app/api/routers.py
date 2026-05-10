from fastapi import APIRouter

router = APIRouter()


@router.get()
def get_user_account():
    return {"message": "user account fetched successfully!"}


@router.post()
def create_user_account():
    return {"message": "user account created successfully!"}


@router.patch()
def update_user_account():
    return {"message": "user account updated successfully!"}


@router.delete()
def delete_user_account():
    return {"message": "user account deleted successfully!"}
