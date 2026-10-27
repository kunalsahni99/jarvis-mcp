from pydantic import BaseModel

class HealthResponse(BaseModel):
    language: str