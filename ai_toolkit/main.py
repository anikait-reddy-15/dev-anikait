import uvicorn
import fastapi

app = fastapi.FastAPI()

if __name__ == "__main__":
    uvicorn.run("Training.main:app", reload=True)
    uvicorn.run("Inference.main:app", reload=True)