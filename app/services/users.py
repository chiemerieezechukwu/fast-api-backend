from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository


async def check_email_is_taken(repo: UsersRepository, email: str) -> bool:
    try:
        await repo.get_user_by_email(email=email)
    except EntityDoesNotExist:
        return False

    return True
