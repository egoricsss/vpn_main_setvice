import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import auth_router
from src.core.config import config


# class App:
#     routers: list[APIRouter] = [auth_router]
#
#     def __init__(self, config) -> None:
#         self._config = config
#
#     def setup_cors(self, application: FastAPI) -> None:
#         application.add_middleware(
#             CORSMiddleware,
#             allow_origins=self._config.api.CORS_ORIGINS,
#             allow_credentials=self._config.api.CORS_CREDENTIALS,
#             allow_methods=self._config.api.CORS_METHODS,
#             allow_headers=self._config.api.CORS_HEADERS,
#         )
#
#     def include_routers(self, application: FastAPI) -> None:
#         for router in self.routers:
#             application.include_router(router)
#
#     def initialize(self) -> FastAPI:
#         application = FastAPI()
#         self.setup_cors(application)
#         self.include_routers(application)
#         return application


app = FastAPI()
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("src.__main__:app", reload=True, host="0.0.0.0")
