from pydantic import BaseModel, Field, ConfigDict

class CategorySchema(BaseModel):
    """
    Model for GET request by Category
    """

    id: int
    name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class CreateCategorySchema(BaseModel):
    """
    Model for POST|PUT|PATCH request by Category
    """
    
    name: str = Field(min_length=2,
                      max_length=50,
                      description="Category's name")
    