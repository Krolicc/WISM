import uuid
from fastapi_users import schemas

# --- User Schemas for FastAPI-Users ---

class UserRead(schemas.BaseUser[uuid.UUID]):
    # This schema is used when reading user data (e.g., GET /users/me)
    pass

class UserCreate(schemas.BaseUserCreate):
    # This schema is used when a new user signs up
    pass

class UserUpdate(schemas.BaseUserUpdate):
    # This schema is used when a user updates their own data
    pass
