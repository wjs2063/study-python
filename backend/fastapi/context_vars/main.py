import uvicorn
from fastapi import FastAPI
from backend.fastapi.context_vars.middleware import request_context,ContextMiddleware


app = FastAPI()
app.add_middleware(ContextMiddleware)

@app.get("/")
async def context_handler():
    print(request_context.get())
    return {"hello": "world"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)