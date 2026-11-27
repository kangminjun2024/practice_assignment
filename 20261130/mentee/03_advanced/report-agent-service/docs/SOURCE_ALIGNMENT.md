# 소스 기준 및 변경 사항
기준: `Day31_20261130_FastAPI_LangChain_Integration_코드연동보완본.html`의 41p Explorer 전체 20개 파일(CODES ide-*), 8개 실습 안내와 3p Workflow. Agent 및 Tool은 `Day30_20261127_Report_Agent_전체_강사용.zip`의 mentor/01_basic에서 가져왔다. 기존 SQL 및 ERD는 Day30 common의 읽기 전용 확인 SQL과 ERD이다. 11/25 ZIP의 mentor/mentee·README/Expected/Review/Test 구조를 참고했다.

- 11/30의 07-B 확장 승인에 따라 AgentService와 Agent Router, 기존 2 Tool을 추가했다. 원래 강의 41p Direct RAG 구조를 유지하되 app/main.py와 Runtime은 통합본이다.
- Direct API 및 Agent API에서 지원하는 명시적 보고서 ID 범위를 DB/GPU/LLM 실행 전 검사한다. 기존 규칙은 `보고서 63`, `RPT-63`, `report id 63` 등만 지원한다. 모든 자연어 숫자를 식별하는 것은 아니다.
- rag_search는 RagService.run()을 공유하고 `.model_dump()`한다. 원 질문에서 인식한 ID가 일부 누락돼도 보존하며 모델이 만든 범위 밖 ID는 Tool 오류로 전달한다. 사용자가 지정한 Category는 RAG 검색 범위이다. lookup_status는 원래 계약대로 보고서 ID의 현재 상태를 읽는다.
- Cross-Encoder 점수 개수 검사 추가(숫자 수가 후보 수와 다르면 실패). 기존 Context 예산은 글자 기준이며 검색은 저장 Overview Vector, 생성은 보고서 본문 기준이다.
- Agent의 필요 Tool 완료 판단은 Day30의 보수적 규칙 기반 검증이며 모델의 Tool 선택을 고정하지 않는다. 임의 자연어 의도를 완벽하게 분류하는 Router가 아니다. 단일 ID Task를 기본 성공 기준으로 사용한다. 복수 ID 질문에서는 Context-k 때문에 모든 보고서가 포함되지 않을 수 있다.
- Direct RAG는 5~300자 질문, Agent는 기존 5~1000자 질문 계약이다. Source 검증은 ID 일치이며 사실성 보증이 아니다. LLM timeout은 한 호출 설정이지 전체 HTTP deadline이 아니다. 각 단계의 Meter는 실제 기록이지만 성공 횟수와 예약한 모델 호출 수는 다를 수 있다.
- 이번 실습의 차이와 추가 부분은 위 내용에 한정하며 원본 강의 HTML을 변경하지 않았다. LangGraph/MCP 직접 구현은 제외한다.

## 재검수 보완
- 공통 RagService에서 검색 전 명시 ID 범위와 검색 후 결과 Query·Source ID·인용·검색 범위 계약을 재검사한다. 실제 Context에 존재하는지의 검사는 여전히 Pipeline이 담당한다. 복수 ID 질문의 Direct RAG는 일부 근거만 답할 수 있으므로 완전성은 사람 검토가 필요하다.
- Tool에 `args_schema`를 명시해 strict Pydantic 계약을 적용한다. `InjectedToolCallId`는 서버 주입 필드이며 모델에 노출되는 업무 인수와 구분한다.
- 07-B는 복합 요청 1회로 두 Tool 및 DB 조회값을 확인하며, 08은 별도 세 Task를 확인한다. Fixture skip은 미완료로 기록한다.
- 비스트리밍 HTTP 경계에서 예상하지 못한 예외를 안전한 500으로 처리한다. 이 조치만으로 SDK/인프라의 모든 로그가 보호되는 것은 아니다.
- 강의 HTML·기존 DB·TODO 위치와 개수는 변경하지 않았다.
