from fastapi import FastAPI

from api.qa_router import router as qa_router


app = FastAPI(
    title="Evaluator-Generator QA System",
    version="1.0.0",
)


app.include_router(qa_router)
