from fastapi import APIRouter
from app.models.qa import QARequest, QAResponse

router = APIRouter()

@router.get("/qa")
async def get_qa_examples():
    """Get example Q&A pairs"""
    return {
        "examples": [
            {"question": "What is FastAPI?", "answer": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints."},
            {"question": "How do you create a React component?", "answer": "You can create a React component using function syntax: function MyComponent() { return <div>Hello World</div>; }"}
        ]
    }

@router.post("/qa", response_model=QAResponse)
async def create_qa(qa_request: QARequest):
    """Create a new Q&A pair"""
    # This is a simple example - in a real app you'd save to a database
    return QAResponse(
        question=qa_request.question,
        answer=f"Answer to: {qa_request.question}",
        id=1
    )
