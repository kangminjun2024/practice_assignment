# Day33 실습 안내 — AI Agent Service Integration

**2026.12.02 (수) · 11월 30일~12월 2일 연속 프로젝트 완성**

기존 FastAPI·LangChain 기반 AI Agent에 AI Tool로 간단한 Frontend를 생성하여 실제 서비스를 완성합니다. Frontend 문법을 모두 직접 작성할 필요는 없습니다. 시스템 구조, API 계약, 코드 변경 범위, 실제 실행 결과를 이해하고 검증하는 것이 중요합니다.

## 1. 공통 준비 사항

### 1-1. 프로젝트 열기

`D33_mentee_v2.zip`을 `C:\workspace`처럼 짧은 경로에 압축 해제합니다. 다음 중 자신의 난이도에 해당하는 `report-agent-service` 폴더를 VS Code에서 엽니다.

```text
D33/mentee/
├── 01_basic/report-agent-service/         # 기본필수
├── 02_intermediate/report-agent-service/  # 응용
└── 03_advanced/report-agent-service/      # 심화
```

이 문서의 모든 명령은 해당 `report-agent-service` 폴더에서 **기존 CUDA 가상환경을 활성화한 Git Bash 터미널**을 기준으로 실행합니다. 실습 01~08은 하나의 프로젝트를 순서대로 발전시키는 과정입니다.

### 1-2. 필요한 패키지 및 환경

| 구분 | 패키지 및 기술 |
|---|---|
| Backend | `fastapi`, `uvicorn`, `pydantic`, `python-dotenv` |
| AI Agent | `langchain`, `langchain-core`, `langchain-openai` |
| Database | `sqlalchemy`, `psycopg[binary]`, `pgvector` |
| GPU 추론 | 기존 CUDA `torch`, `sentence-transformers` |
| 테스트 및 HTTP 요청 | `pytest`, `httpx` |
| Frontend | HTML, CSS, Vanilla JavaScript, Browser (별도 패키지 불필요) |

기존 Day32 환경이 정상이라면 패키지를 다시 설치할 필요가 없습니다. 설치가 필요한 경우에만 기존 CUDA PyTorch 버전을 보호한 상태로 진행합니다. 구체적인 버전 범위는 제공된 `requirements.txt`를 따릅니다.

```bash
python -m tools.preserve_torch
python -m pip install -r requirements.txt -c outputs/torch_constraints.txt
python -m pip check
```

첫 번째 명령이 실패하면 설치를 진행하지 말고 기존 CUDA 가상환경을 먼저 확인합니다. 의존성 충돌을 해결하기 위해 PyTorch를 임의로 재설치하지 않습니다. React, Vue, npm, Docker, 별도 Frontend 개발 서버는 필요하지 않습니다.

### 1-3. 환경변수와 DB 확인

```bash
# .env가 없을 때만 생성합니다.
test -f .env || cp .env.example .env
```

`.env`에 이전 실습에서 사용하던 `DATABASE_URL`, `OPENAI_API_KEY`, `LLM_MODEL`을 설정합니다. 기존 `report_agent_lab` DB, pgvector, E5 Embedding 및 Cross-Encoder Reranker의 CUDA 환경을 유지합니다. 신규 DB 생성이나 재인덱싱은 하지 않습니다.

```bash
python -m tools.check_environment
python -m tools.check_report_db --report-id 63 --missing-id 999999
```

- `eligible=true`: 해당 보고서가 RAG 검색에 사용 가능한지 확인합니다.
- `missing_id_confirmed=true`: 테스트용 부재 ID가 실제 존재하지 않는지 확인합니다.
- 63번, 999999번, `RAG`는 예시입니다. 실제 적격 ID, 부재 ID, 제목 검색에 존재하는 Keyword를 선택합니다. 보고서 ID는 JavaScript 안전 정수 범위 내에서 사용합니다.
- 예시 값을 변경했다면 `tools.run_lab`의 Live 실행에 `--report-id`, `--missing-id`, `--keyword`를 동일하게 지정하고, `tools.record_capture`에도 같은 `--report-id`, `--keyword`를 지정합니다. Keyword는 따옴표나 줄바꿈이 없는 1~100자 문자열로 사용합니다.

`/health` 및 환경 점검은 준비 상태를 확인하는 기능이며 실제 LLM 인증이나 추론 성공을 보장하지 않습니다.

## 2. 전체 실습 흐름

| 실습 | 강의 페이지 | 실습 폴더 (`labs/` 아래) | 시간 | 실행 환경 |
|---|---:|---|---:|---|
| 01. Backend Baseline & Architecture | 8 | `01_baseline` | 10분 | 기존 Backend, 실제 DB·LLM |
| 02. API Contract & Communication | 17 | `02_contract` | 10분 | FastAPI, Pydantic, pytest |
| 03. Requirements & AI Prompt | 23 | `03_prompt` | 15분 | AI Tool, pytest |
| 04. AI Code Generation & Integration | 31 | `04_generate` | 20분 | AI Tool, Browser, Fixture 및 Live |
| 05. Code Review & Error Handling | 38 | `05_review` | 15분 | Browser, Fixture, pytest |
| 06. Agent Result Visualization | 44 | `06_results` | 15분 | Browser, Fixture, pytest |
| 07. End-to-End Integration & Debugging | 51 | `07_integration` | 25분 | Browser, 실제 CUDA·DB·LLM |
| 08. Final Verification & Delivery | 56 | `08_verify` | 15분 | 전체 환경, pytest |

## 3. 서버 실행 방법 — 공통

| 구분 | 실행 명령 | 접속 주소 | 용도 |
|---|---|---|---|
| 실제 서버 (Live) | `python -m app.main` | http://127.0.0.1:8000/ | 실제 Agent 업무 실행 |
| Swagger UI | 실제 서버 실행 상태 | http://127.0.0.1:8000/docs | API 계약 확인 |
| Fixture 서버 | `python -m tools.fixture_server` | http://127.0.0.1:8010/__cases | 가상 응답을 이용한 UI 테스트 |

실제 서버를 실행하는 터미널 A와 실습 명령을 실행하는 터미널 B를 구분합니다. 서버 종료는 `Ctrl+C`입니다. Frontend를 생성하기 전(실습 01~03)에는 `/docs`를 이용합니다.

Fixture 서버는 Python 표준 라이브러리로 동작하며 실제 DB·GPU·LLM을 호출하지 않습니다. **Fixture 실행 전 실제 8000 서버를 종료하고**, 생성된 코드가 외부 API를 임의 호출하지 않는지 검토합니다. 8010의 제어 화면에서 사례를 선택하고 질문을 복사한 뒤 테스트 UI 링크를 열어 지정된 Category로 전송합니다. Network의 요청 URL이 8010인지 확인하고 `/__last`에서 `last.payload_matches=true`, 요청 횟수(`calls`)를 확인합니다. Fixture 서버는 임의 JavaScript의 네트워크 접근을 제한하는 Sandbox가 아닙니다.

실제 Browser의 질문 전송에는 LLM 비용이 발생할 수 있습니다. `--allow-paid-llm`은 실행기의 추가 모델 호출에 대한 동의 옵션이며 Browser의 전송을 제한하는 기능이 아닙니다.

---

## 실습 01. Backend Baseline & Architecture

**개요:** 기존 Day32 Agent가 정상 작동하는지 확인하고, API·Service·AI/Tool·Data Access Layer와 실제 파일을 연결합니다.

**필요 환경:** 기존 CUDA 가상환경, PostgreSQL/pgvector, LangChain, 실제 LLM API.

1. 공통 환경 점검을 완료합니다.
2. 터미널 A에서 서버를 시작하고 `/docs`와 `/health`를 확인합니다.

```bash
python -m app.main
```

3. 터미널 B에서 기존 Agent의 상태 조회(T02)와 유형별 집계(T05)를 실제 실행합니다.

```bash
python -m tools.run_lab 01 --live --allow-paid-llm
```

응용·심화는 Direct RAG API도 추가 확인합니다. 이 명령은 실제 모델을 호출합니다.

**완료 기준:** 기존 업무의 `completed`, 실제 Tool 실행, `outputs/db_before.json`과 `baseline_T02.json`, `baseline_T05.json`, `lab_01_live.json`을 확인합니다. 계층 구조와 파일 간 관계를 실습 활동지에 정리한 후 서버를 종료합니다.

## 실습 02. API Contract & Communication

**개요:** Frontend가 보내는 Request JSON과 서버가 반환하는 Response JSON의 계약을 확인합니다.

**필요 환경:** FastAPI, Pydantic, pytest. 자동 검사에는 실제 LLM 호출이 필요하지 않습니다.

```bash
# 터미널 A: 종료했던 서버를 다시 실행
python -m app.main
```

Swagger UI(`/docs`)에서 `POST /api/v1/agent/ask`를 확인하고 `app/schemas/agent.py`, `app/schemas/rag.py`, `prompts/context.json`을 비교합니다.

```bash
# 터미널 B
python -m tools.run_lab 02
```

**확인 사항:** `question`, `category_code`(전체는 `null`), `answer`, `sources`, `tool_trace`, `tool_results`의 역할. HTTP 200과 업무 상태(`completed`, `insufficient_evidence`, `incomplete`)는 서로 다른 의미입니다.

**완료 기준:** `outputs/api_contract.md`에 URL·Method·Header·Body 및 응답 상태의 의미를 작성합니다. 서버를 종료합니다.

## 실습 03. Requirements & AI Prompt

**개요:** AI Tool에 전달할 요구사항과 구현 계획을 정리합니다. 코드를 생성하기 전에 변경 범위를 먼저 확인합니다.

**필요 환경:** 사용 가능한 AI Tool(IDE 기반 또는 채팅형), 기존 Python 테스트 환경.

다음 파일을 확인하여 AI에게 필요한 Context를 제공합니다.

- `prompts/requirements.md` — UI 기능 요구사항
- `prompts/context.json` — 실제 API Schema 및 가상 응답
- `prompts/plan.md` — 구현 계획 요청
- `docs/MAIN_PATCH.md` — FastAPI 정적 파일 제공 최소 변경안

기본필수는 제공된 요구사항을 활용합니다. 응용은 표시·오류 기준을 보완하고, 심화는 `prompts/requirements_template.md`를 바탕으로 직접 요구사항을 작성합니다.

```bash
python -m tools.run_lab 03
```

**완료 기준:** `outputs/requirements.md`, `outputs/ai_worklog.md`에 요구사항·AI 구현 계획·승인한 변경 파일을 기록합니다. AI Tool에는 `.env`, 실제 보고서, `outputs/`, 민감 로그가 없는 별도 작업 복사본만 제공합니다. 자동 설치, DB 변경, 실제 API 호출은 승인하지 않습니다.

## 실습 04. AI Code Generation & Integration

**개요:** AI Tool을 이용하여 HTML·CSS·Vanilla JavaScript 화면을 생성하고 기존 FastAPI에 연결합니다.

**필요 환경:** AI Tool, Browser, FastAPI, 기존 Python 환경. Live 확인 시 실제 DB·LLM이 필요합니다.

1. 승인한 구현 계획과 `prompts/build.md`, `context.json`, `docs/MAIN_PATCH.md`를 AI에 전달합니다.
2. `app/static/index.html`, `app/static/styles.css`, `app/static/app.js` 세 파일을 생성하고 `app/main.py`에 제공된 최소 Patch를 적용합니다. 기존 Backend·API Schema·패키지·테스트는 수정하지 않습니다.
3. 변경 범위와 정적 파일 제공을 검사합니다.

```bash
python -m tools.check_changes
python -m tools.run_lab 04
```

4. Fixture 서버에서 `count` 사례를 선택하여 전송하고 `/__last`에서 실제 수신 요청을 확인합니다.

```bash
python -m tools.fixture_server
```

5. Fixture 서버를 종료한 후 실제 서버를 시작합니다. Browser에서 T05(유형별 등록 건수)를 실제 전송하고, 아래 공통 캡처 절차에 따라 응답을 저장합니다.

```bash
# 터미널 A
python -m app.main
# 터미널 B: T05.json 저장 이후
python -m tools.record_capture T05
python -m tools.run_lab 04 --live
```

**완료 기준:** 세 정적 파일 제공, 기존 Backend 보존, Fixture 요청 1건 확인, 실제 T05의 Network 응답과 화면 일치. 04의 Live 검사 자체는 추가 LLM 호출 없이 저장된 응답을 DB와 대조합니다.

## 실습 05. Code Review & Error Handling

**개요:** AI 생성 코드의 변경 범위와 정상·실패 처리 과정을 검토합니다.

**필요 환경:** Browser DevTools, Fixture 서버(Python 표준 라이브러리), pytest, AI Tool. 실제 LLM 호출은 불필요합니다.

```bash
python -m tools.check_changes
# 실제 서버(8000)를 종료한 후 실행
python -m tools.fixture_server
```

8010의 제어 화면에서 `count` 정상 응답 이후 `timeout`, `invalid` 사례를 시험합니다. 응용·심화는 `db503`, `network`, `badjson`, `partial`, `bodyfail`, `httphtml` 등 `docs/fixture_guide.md`의 추가 사례를 확인합니다. 실패 후 입력과 버튼이 복구되고 이전 결과가 제거되는지, 처리 중 중복 요청이 발생하지 않는지 확인합니다.

오류를 발견했다면 `prompts/fix.md`에 재현 조건·기대 결과·실제 결과·수정 범위를 작성해 AI에게 최소 수정만 요청합니다.

```bash
python -m tools.run_lab 05
```

**완료 기준:** 보호 파일 변경 없음, 정상·실패 화면 검토, 수정한 사례 재시험. `outputs/review.md`에 확인 결과를 기록합니다.

## 실습 06. Agent Result Visualization

**개요:** 실제 API 계약의 데이터를 화면에 정확하게 표시하는지 확인합니다.

**필요 환경:** Browser, Fixture 서버, pytest. 실제 DB·LLM 호출은 불필요합니다.

Fixture 서버(8010)를 유지하거나 다시 실행하고 다음 사례를 선택합니다.

| 사례 | 확인할 화면 |
|---|---|
| `rag` | 답변·RAG Sources·Tool Trace |
| `status`, `falseflag` | 인덱싱 상태·Revision·`embedding_fresh=false` |
| `title` | 제목 검색 결과 목록(최대 5건) |
| `detail`, `truncated` | 상세 정보·최대 3,000자 Preview 및 잘림 여부 |
| `count`, `category_count` | 0건 집계 및 지정 Category의 요청·결과 |
| `seq`, `compound` | 순차 조회 및 복합 업무 결과 |
| `empty`, `partial` | 근거 부족·미완료 및 부분 결과 표시 |

`category_count`에서는 제어 화면에 지정된 `RESEARCH_PLAN`을 선택합니다. 응용·심화는 `badshape`, `bigint`, `xss` 등 잘못된 자료형·누락 필드·안전하지 않은 HTML 문자열 처리도 확인합니다.

```bash
python -m tools.run_lab 06
```

**완료 기준:** JSON의 실제 필드와 화면 표시가 일치하고, 0·false가 누락되지 않으며, 오류 응답이 완료로 표시되지 않습니다. `outputs/ui_results.md`에 비교 결과를 기록합니다. 실습 후 Fixture 서버를 종료합니다.

## 실습 07. End-to-End Integration & Debugging

**개요:** AI가 생성한 Frontend에서 실제 Agent를 실행하고 Browser부터 DB·GPU·LLM까지 이어지는 흐름을 확인합니다.

**필요 환경:** 실제 FastAPI·CUDA·PostgreSQL/pgvector·LangChain·LLM API, Browser DevTools, httpx.

```bash
# Fixture 서버를 종료하고 변경 범위를 확인
python -m tools.check_changes
# 터미널 A
python -m app.main
```

http://127.0.0.1:8000/ 에서 F12 → Network를 열고 기본필수는 T01·T05, 응용·심화는 T01·T05·T06·T07을 실제 전송합니다. 질문은 `docs/tasks.md`를 그대로 사용하고 Category는 전체(null)로 선택합니다.

각 응답을 아래 공통 캡처 절차에 따라 저장·등록한 뒤 검증합니다.

```bash
# 터미널 B: 필요한 실제 응답을 모두 저장한 후
python -m tools.record_capture T01
python -m tools.record_capture T05
# 응용·심화는 T06, T07도 각각 등록
python -m tools.run_lab 07 --live
```

**완료 기준:** 실제 UI 요청·응답·화면·Tool 결과가 일치합니다. 순차 업무는 선행 제목 검색의 첫 ID와 후속 상세 조회 ID를 비교합니다. 저장된 응답을 이용하는 Live 검증은 모델을 추가 호출하지 않습니다.

## 실습 08. Final Verification & Delivery

**개요:** 7개 실제 대표 업무, 기존 API, DB 불변성을 확인하고 완성된 서비스를 정리합니다.

**필요 환경:** 전체 실제 실행 환경 및 pytest. 추가 Direct RAG 검증에 LLM 비용이 발생할 수 있습니다.

모든 난이도에서 아래 7개 업무를 검증합니다. 앞선 실습에서 동일 UI 버전·동일 Task 조건으로 저장한 응답은 재사용 가능합니다. 아직 실행하지 않은 업무만 추가로 전송하고 각각 응답을 등록합니다.

| ID | 업무 | 필요한 Tool |
|---|---|---|
| T01 | 보고서 핵심 내용 | `rag_search` |
| T02 | 현재 인덱싱 상태 | `lookup_status` |
| T03 | 제목 Keyword 검색 | `search_by_title` |
| T04 | 보고서 상세 조회 | `get_report_detail` |
| T05 | 유형별 등록 건수 | `count_reports_by_category` |
| T06 | 제목 검색 후 첫 보고서 상세 조회 | `search_by_title` → `get_report_detail` |
| T07 | 핵심 내용 및 현재 상태 | `rag_search` + `lookup_status` |

```bash
# 실제 서버가 실행 중이고 7개 응답을 모두 등록한 상태
python -m tools.run_lab 08 --live --allow-paid-llm
```

**완료 기준:** T01~T07 실제 응답 검증, Direct RAG 회귀 검사, HTTP 422, 실습 전후 DB Snapshot 비교. `outputs/lab_08_checks.json`, `lab_08_live.json`의 결과와 `prompts/acceptance.md`를 확인하고 `outputs/acceptance.md`, `outputs/verification.md`를 작성합니다. DB Snapshot이 달라지면 다른 사용자의 변경 여부부터 확인하며 데이터를 임의로 수정하지 않습니다.

---

## 4. 실제 응답 저장 및 등록 방법 (실습 04·07·08 공통)

1. 실제 8000 서버에 접속하여 F12 → Network에서 `/api/v1/agent/ask` 요청을 선택합니다.
2. Request Payload와 HTTP Status를 확인하고, Response 탭의 **실제 JSON 전체**를 `outputs/live/` 폴더에 UTF-8 파일로 저장합니다. 폴더가 없다면 생성합니다. 예를 들어 T05는 `outputs/live/T05.json`입니다.
3. 화면에 표시된 값과 실제 JSON을 비교합니다. 응답 상태가 `completed`가 아니거나 Tool 결과가 부족하면 실패 또는 미완료로 기록합니다.
4. 실제 서버가 실행 중인 상태에서 해당 업무를 등록합니다.

```bash
python -m tools.record_capture T05
# 예: 적격 보고서 ID를 변경한 경우 (실제 값에 맞춰 사용)
# python -m tools.record_capture T05 --report-id 64 --keyword RAG
```

등록하면 `T05.meta.json`에 현재 UI 버전과 응답 Hash, 업무 조건이 기록됩니다. UI가 수정되면 이전 버전의 캡처는 다시 사용할 수 없으므로 실제 요청을 재검증합니다. 등록 명령은 LLM을 호출하지 않으며, 저장된 응답의 출처나 화면을 자동 인증하지도 않습니다. 실제 Network 및 DOM 확인은 직접 해야 합니다.

## 5. 실습 완료 및 유의 사항

- 각 실습의 `labs/.../expected/EXPECTED.md`를 확인하고 `reports/review.md`에 결과를 기록합니다. 자동 검사 결과는 `outputs/lab_XX_checks.json`, 실제 검증은 `outputs/lab_XX_live.json`에서 확인합니다.
- `passed`, `failed`, `incomplete`를 구분합니다. pytest의 skip은 미검증입니다. 자동 검사만 통과하거나 Fixture에서 정상 표시된 것만으로 실제 서비스 완료가 되지는 않습니다.
- `.env`, DB 접속 정보, API Key, 실제 보고서 원문 및 `outputs/`의 민감 데이터는 외부 AI Tool이나 공개 Git에 공유하지 않습니다. 제출할 때는 민감정보를 제거한 검증 요약을 사용합니다.
- 오류 해결이 어려우면 `docs/VERIFY.md`, `docs/fixture_guide.md`, 해당 실습 README를 참고합니다. 실제 LLM 실패를 반복 호출하여 재현하지 않습니다.

**이번 실습의 평가 기준은 강사용 코드와의 일치가 아닙니다. AI Tool로 구현했더라도 시스템의 구조를 이해하고 실제 API·Tool·DB 결과와 화면이 정확히 연결되는지 확인하는 것이 목표입니다.**
