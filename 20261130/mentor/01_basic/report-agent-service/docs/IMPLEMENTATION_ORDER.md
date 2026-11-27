# 구현 흐름
## 요청 실행과 구현 순서는 다르다
구현은 Settings/Schema → Runtime → DB/GPU → Context → LCEL → Service → API → Agent → Verification 순으로 진행한다. 각 README에서 TODO가 있는 실제 파일을 열어 구현한다.

| 단계 | 핵심 파일 | 확인할 입출력 |
|---|---|---|
| API | app/main.py, app/api/rag.py, app/schemas/rag.py | HTTP JSON → RagAskRequest → 응답 |
| Runtime | app/core/runtime.py | Settings/DI → 공용 RagService, AgentService |
| DB | app/db/connection.py, app/db/repository.py | Vector/조건 → SQL Rows |
| AI Core | app/rag/embeddings.py, retriever.py, reranker.py | 질문 → Vector → Document → 순위 |
| RAG | app/rag/pipeline.py | Context → ChatPromptValue → AIMessage → RagResult dict |
| Service | app/services/rag_service.py | RagResult → RagAskResponse |
| Agent | app/agent.py, app/tools/*, app/api/agent.py | Task → ToolMessage → Ledger 검증 → AskResponse |
| 검증 | tools/acceptance.py | 실제 HTTP 응답 → 구조 검증 |

## Direct RAG 요청
FastAPI(Pydantic) → 명시 ID 범위 검사 → Runtime.health → RagService.ask(새 Meter) → RagService.run → Pipeline.retrieve → E5 CUDA → Repository SELECT → Reranker CUDA → Context → LCEL invoke → Parser/Citation → RagResult → Response Schema.

## Agent 요청
FastAPI → Runtime.health → 새 Meter → AgentService.ask → create_agent(두 Tool, Model/Tool Limit Middleware) → 모델 판단 → rag_search 또는 lookup_status 또는 복수 호출 → 동일 요청의 ToolMessage 및 Ledger 대조 → finalize → AskResponse. rag_search는 RagService.run을 직접 호출하고 결과를 dict로 변환한다. lookup_status는 Repository.lookup으로 DB를 읽는다. RAG 호출 시 Agent 모델 호출과 RAG 생성 모델 호출을 같은 Meter에 기록한다. 미실행 Tool을 실행했다고 기록하지 않는다. 내일 5개 Tool을 추가할 때 기존 RAG 기능은 유지한다.

## 상태 처리
Direct RAG: found→completed, not_found→insufficient_evidence. Agent: 실제 결과와 필요한 Tool을 기준으로 completed/insufficient_evidence/incomplete. 422는 사용자 Schema/ID 범위 오류, 503은 준비/외부 의존성 오류, 504는 LLM Timeout, 500은 출력/Tool 계약 오류 등. 404/405는 FastAPI 기본 HTTP 오류 형식일 수 있다. 전역 적격 Vector 0개는 Preflight 실패 503이며, 특정 ID의 후보 없음은 200이다.

## 테스트 확인
실제 LCEL 및 create_agent를 사용하는 SDK 테스트는 LangChain 패키지가 설치되어야 실행된다. Fixture는 DB/GPU/외부 LLM 대신 테스트 객체를 주입하며 실제 성공 증거가 아니다. `outputs/lab_*_fixture.json`은 JUnit XML의 통과·실패·skip 수를 기록한다. 일부 skip도 미완료로 처리하며, 실제 연동 성공을 의미하지 않는다.
