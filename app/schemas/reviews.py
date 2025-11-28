from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone

class ReviewSchema(BaseModel):
    """
    Model for GET request by Reviews
    """

    id: int
    buyer_id: int
    product_id: int
    comment: str | None = Field(default=None)
    comment_date: datetime = Field(default_factory=datetime.now,
                                   description='Date and time review')
    grade: int 
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ReviewsCreateSchema(BaseModel):
    """
    Model for POST|PUT|PATCH request by Reviews
    """
    
    product_id: int
    comment: str | None = Field(default=None)
    comment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                   description='Date and time review')
    grade: int = Field(ge=1, le=5)


class ReviewsUpdateSchema(BaseModel):
    """
    Model for PUT|PATCH request by Reviews
    """
    
    comment: str | None = Field(default=None)
    comment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                   description='Date and time review')
    grade: int = Field(ge=1, le=5)