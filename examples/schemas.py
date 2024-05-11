from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class DepartmentQuery(BaseModel):
    order_by: List[str] = Field(default_factory=list)


class DepartmentIn(BaseModel):
    title: str


class DepartmentOut(BaseModel):
    id: UUID
    title: str
