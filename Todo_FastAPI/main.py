import uvicorn
import fastapi

app = fastapi.FastAPI()

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)