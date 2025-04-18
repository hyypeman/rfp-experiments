from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
from typing import Dict
from contextlib import asynccontextmanager
import logging
import shutil
import uvicorn
from main import (
    run_workflow,
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RFP Analysis API")
    yield
    logger.info("Shutting down RFP Analysis API")

app = FastAPI(
    title="RFP Analysis API",
    description="API for analyzing RFP documents using LangGraph and Claude",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create file_storage directory if it doesn't exist
STORAGE_DIR = Path("file_storage")
STORAGE_DIR.mkdir(exist_ok=True)

class PdfContent(BaseModel):
  pdf_file_content: str

@app.post("/analyze")
async def analyze_rfp(request: PdfContent) -> Dict:
    """
    Analyze an RFP document.
    
    Args:
        request: The request containing the PDF file content
        
    Returns:
        Dict containing the analysis results
    """
    print(f"PDF content: {request.pdf_file_content[:30]}")
    # if not file.filename.endswith('.pdf'):
    #     raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # # Save the uploaded file
    # file_path = STORAGE_DIR / file.filename
    # try:
    #     with file_path.open("wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    
    try:
        # Create initial state
        initial_state = {
            "pdf_filename": None,
            "pdf_data": request.pdf_file_content,
            "current_stage": 0,
            "previous_output": None,
            "final_table": None,
            "stage_outputs": {},
        }

        # Run the workflow
        result = run_workflow(initial_state)
        
        # Clean up the uploaded file
        # try:
        #     file_path.unlink()
        # except Exception as e:
        #     logger.warning(f"Could not delete uploaded file: {str(e)}")
        
        return {
            "status": "success",
            "results": result["stage_outputs"],
            "final_table": result.get("final_table")
        }
    except Exception as e:
        # Clean up the uploaded file in case of error
        # try:
        #     file_path.unlink()
        # except Exception as cleanup_error:
        #     logger.warning(f"Could not delete uploaded file: {str(cleanup_error)}")
        logger.error(f"Error analyzing RFP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=2500, reload=True)
