from pydantic import BaseModel


class RWSchema(BaseModel):
    class Config:
        orm_mode = True
