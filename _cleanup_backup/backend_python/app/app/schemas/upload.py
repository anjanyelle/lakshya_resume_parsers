from pydantic import BaseModel


class UploadJobResponse(BaseModel):
    job_id: str
    status: str


class BatchUploadResponse(BaseModel):
    message: str
    jobs: list[UploadJobResponse]
