from app.core.settings import load_settings
from app.db.connection import Database
from app.db.repository import Repository
from app.rag.embeddings import E5
from app.rag.retriever import Retriever
from app.rag.reranker import Reranker
from app.rag.pipeline import RagPipeline
from app.core.models import make_model
from app.services.rag_service import RagService
from app.core.preflight import preflight
from app.agent import AgentService

class Runtime:
    def __init__(self, settings=None, repo=None, embedder=None,
                 reranker=None, model_factory=None):
        self.settings = settings or load_settings()
        self.db = None if repo is not None else Database(self.settings)
        # BEGIN D31-A03-03
        # 해설 D31-A03-03: DI를 이용하여 실제 DB 연결과 테스트용 의존 객체를 구분한다.
        self.repo = repo if repo is not None else Repository(self.db)
        # END D31-A03-03
        self.embedder = embedder if embedder is not None else E5(self.settings)
        self.reranker = reranker if reranker is not None else Reranker(self.settings)
        # BEGIN D31-A03-04
        # 해설 D31-A03-04: 함수 참조를 보관한다. make_model을 지금 실행하여 LLM 객체를 미리 생성하지 않는다.
        self.model_factory = model_factory or (lambda: make_model(self.settings))
        # END D31-A03-04
        # 기존 RAG 기능을 조립하고 신규 Service에 전달한다.
        self.pipeline = RagPipeline(
            self.settings, Retriever(self.repo, self.embedder),
            self.reranker, self.model_factory,
        )
        # BEGIN D31-A03-01
        # 해설 D31-A03-01: 같은 Runtime의 Pipeline을 Direct API와 Agent가 공유한다.
        self.rag_service = RagService(self.settings, self.pipeline)
        # END D31-A03-01
        # Agent는 동일한 RagService와 Repository를 공유한다. 요청 처리 때 Agent를 구성한다.
        self.agent = AgentService(self.settings, self.repo, self.rag_service, self.model_factory)

    def health(self):
        # BEGIN D31-A03-02
        # 해설 D31-A03-02: Health Check는 실제 모델 로드나 유료 API 호출이 아니다.
        return preflight(self.settings, self.repo)
        # END D31-A03-02

    def close(self):
        if self.db:
            self.db.close()
