import uvicorn
from fastapi import FastAPI
from log_config import log

app = FastAPI()


@app.get("/")
async def root():
    log.info({"message": "efk_app"})
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)