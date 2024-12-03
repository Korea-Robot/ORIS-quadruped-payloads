from fastapi import FastAPI
from api.inference import router
from config.config import config

app = FastAPI(
    title=config['app']['title'],
    description=config['app']['description'],
    version=config['app']['version']
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config['app']['host'], port=config['app']['port'])
