"""
Entry point for the Process Semantic Layer API.
Starts the FastAPI server using uvicorn.
"""
import uvicorn

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Starting uvicorn server...")
    print("="*60 + "\n")
    
    uvicorn.run(
        "src.api:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="info"
    )
