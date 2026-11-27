# 실습 07. Backend & Agent Integration
강의 43페이지 대응 · 25분 · 01_basic · 수강생용

## 목표
A: Direct RAG / B: 기존 2-Tool Agent 연결

## 수정 위치 및 순서
app/services/rag_service.py, app/api/rag.py, app/api/agent.py, app/agent.py, app/tools/rag_tool.py, app/tools/db_tool.py

- `D31-B07-01` · `app/services/rag_service.py` (07-A) — 공통 업무 함수에서 Pipeline을 호출하고 반환값을 raw에 저장하세요.
- `D31-B07-02` · `app/services/rag_service.py` (07-A) — 현재 요청 질문·Category와 설정된 context_k, 요청 전용 Meter로 run을 실행하세요.
- `D31-B07-03` · `app/tools/rag_tool.py` (07-B) — 공통 RagService의 run을 호출하고 Pydantic 결과를 dict로 변환하세요.
- `D31-B07-04` · `app/api/agent.py` (07-B) — 현재 Runtime의 Agent에 요청 ID, 요청 Body, Meter를 전달하세요.

## 실행 (프로젝트 루트 Terminal)
```bash
# A의 TODO를 먼저 완성한 뒤 검증
python -m tools.run_lab 07 --part A
# 서버 시작 후 다른 Terminal에서 실행 (실제 LLM 비용)
python -m tools.run_lab 07 --part A --live --allow-paid-llm --report-id 63
# B의 TODO 완성, 서버 재시작 후 검증
python -m tools.run_lab 07 --part B
python -m tools.run_lab 07 --part B --live --allow-paid-llm --report-id 63
```

## 완료 기준
실제 Uvicorn 서버에서 Direct RAG와 Agent API 확인. A 완료 후 B 진행

## 산출물 (`outputs/`)
lab_07_A_live.json, lab_07_B_live.json

실습 07-A를 완료한 후 서버를 `python -m app.main`으로 실행합니다. 07-B의 미완성 Agent는 호출하지 않습니다. B 수정 후 서버를 Ctrl+C로 종료하고 재실행합니다. 두 Tool의 순서는 강제하지 않습니다. 07-B에서는 복합 요청 한 번으로 두 Tool 및 DB 조회값을 검사합니다. 08에서 내용·상태·복합 요청을 각각 검증합니다.

**실제 DB에서 적격 ID를 확인하여 63을 바꿀 수 있습니다.** `--missing-id`도 실제 부재를 확인한 값으로 변경하세요. `--live` 없는 명령은 Fixture 테스트입니다. skip은 통과가 아닙니다. 이전 실습의 TODO를 유지하고 새 프로젝트를 만들지 않습니다.
