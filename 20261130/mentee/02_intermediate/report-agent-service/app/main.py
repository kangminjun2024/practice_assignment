"""B-01/B-12: python -m app.main 또는 uvicorn app.main:app."""
from contextlib import asynccontextmanager
from threading import Lock
import logging
from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from app.api.rag import router as rag_router
from app.api.agent import router as agent_router
from app.services.errors import ServiceError

def create_app(runtime_factory=None):
    # Lazy DI: import/Swagger/422 검증에 DB·GPU·키가 없어도 된다.
    if runtime_factory is None:
        def runtime_factory():
            from app.core.runtime import Runtime
            return Runtime()
    holder={};lock=Lock()
    def get_runtime():
        with lock:
            if 'runtime' not in holder:
                holder['runtime']=runtime_factory()
            return holder['runtime']
    @asynccontextmanager
    async def lifespan(app):
        try:
            yield  # Application 동작 구간
        finally:
            if 'runtime' in holder:
                holder.pop('runtime').close()
    app=FastAPI(title='Day31 Report Agent Service',version='1.0',lifespan=lifespan)
    app.state.get_runtime=get_runtime
    @app.exception_handler(ServiceError)
    async def known(request,exc):
        return JSONResponse(status_code=exc.http_status,content=exc.envelope())
    @app.exception_handler(RequestValidationError)
    async def invalid(request,exc):
        return JSONResponse(status_code=422,content=ServiceError('VALIDATION_ERROR').envelope())
    @app.exception_handler(NotImplementedError)
    async def todo(request,exc):
        return JSONResponse(status_code=500,content=ServiceError('NOT_IMPLEMENTED').envelope())
    @app.exception_handler(ResponseValidationError)
    async def invalid_response(request,exc):
        return JSONResponse(status_code=500,content=ServiceError('OUTPUT_CONTRACT_ERROR','response_schema').envelope())
    @app.middleware('http')
    async def safe_unexpected_error(request,call_next):
        # 일반 Exception 처리기만으로는 ASGI 서버가 원본 traceback을 기록할 수 있다.
        # 현재의 비스트리밍 HTTP API에서는 여기에서 예외를 종료하고 안전한 종류만 기록한다.
        try:
            return await call_next(request)
        except Exception as exc:
            logging.getLogger('uvicorn.error').error('unexpected request error type=%s',type(exc).__name__)
            return JSONResponse(status_code=500,content=ServiceError('INTERNAL_ERROR','internal_error').envelope())
    @app.get('/health')
    def health():
        return get_runtime().health()
    # BEGIN D31-I02-02
    # TODO D31-I02-02: FastAPI app에 RAG Router를 등록하세요.
    pass  # UNIMPLEMENTED_D31-I02-02
    # END D31-I02-02
    app.include_router(agent_router)
    return app
app=create_app()
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8000,access_log=False)
