"""기존 CUDA venv와 DB/LLM 설정을 확인한다. 유료 호출 없음."""
import importlib.metadata as md
import sys
from app.core.settings import load_settings
from app.core.preflight import require_cuda, preflight
from app.db.connection import Database
from app.db.repository import Repository
from tools.common import save, safe_error

PACKAGES = ['fastapi','uvicorn','sqlalchemy','psycopg','pgvector','pydantic','python-dotenv','sentence-transformers','langchain','langchain-core','langchain-openai','torch','pytest','httpx']

def inspect_environment():
    versions = {}
    for name in PACKAGES:
        try: versions[name] = md.version(name)
        except md.PackageNotFoundError: versions[name] = None
    missing=[name for name,version in versions.items() if version is None]
    if missing:
        print('미설치 필수 패키지:', ', '.join(missing))
        from app.services.errors import ServiceError
        raise ServiceError('CONFIG_INVALID','missing_packages')
    # 버전이 조회된다고 import/API 호환성이 보장되는 것은 아니다.
    # 모델 객체나 외부 API를 호출하지 않고 필요한 SDK 심볼만 확인한다.
    try:
        from sentence_transformers import SentenceTransformer, CrossEncoder
        from langchain.agents import create_agent
        from langchain.agents.middleware import wrap_model_call, ToolCallLimitMiddleware, ModelCallLimitMiddleware
        from langchain_core.tools import InjectedToolCallId, ToolException
        from langchain_openai import ChatOpenAI
    except Exception as exc:
        from app.services.errors import ServiceError
        print('SDK import 실패:', type(exc).__name__, '기존 CUDA venv 및 패키지 호환성을 확인하세요.')
        raise ServiceError('CONFIG_INVALID','sdk_import_failed') from None
    import torch
    settings = load_settings()
    gpu = require_cuda()
    db = Database(settings)
    try:
        health = preflight(settings, Repository(db))
        return {'mode':'live_preflight_no_llm','python':sys.version.split()[0], 'python_executable':sys.executable,
                'packages':versions,'cuda':torch.version.cuda,'gpu':gpu,'gpu_name':torch.cuda.get_device_name(0),
                'llm_configured':settings.llm_configured,'health':health}
    finally: db.close()

def main():
    try:
        value = inspect_environment(); save('environment.json',value)
        print('준비 확인:',value['gpu'],value['health']['database'],'LLM 인증/추론 미검증')
        return 0
    except Exception as exc: print(safe_error(exc)); return 1
if __name__=='__main__': raise SystemExit(main())
