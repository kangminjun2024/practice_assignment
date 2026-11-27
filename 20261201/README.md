# Day32 | LangChain Agent & Tool Control

**2026.12.01 (화) · 수강생 실습 안내**

전날 완성한 FastAPI 기반 AI Agent에 신규 Tool 3개를 연결하여, 실제 업무에 필요한 Tool을 선택하고 실행하는 5개 Tool 기반 Agent를 완성합니다. 오늘 완성한 프로젝트는 다음 날 Frontend 연동에 사용합니다.

## 1. 실습 준비

1. `D32_mentee.zip`을 `C:\work`처럼 짧은 경로에 압축 해제합니다.
2. `D32/mentee/`에서 자신의 난이도를 하나 선택합니다.
   - `01_basic`: 기본필수 (TODO 15개)
   - `02_intermediate`: 응용 (TODO 22개)
   - `03_advanced`: 심화 (TODO 29개)
3. 선택한 난이도의 `report-agent-service/` 폴더를 VS Code에서 열고, Git Bash 터미널에서 기존 CUDA 가상환경을 활성화합니다. `baseline_day31/` 폴더는 삭제하거나 이동하지 않습니다.

```bash
python -m tools.preserve_torch
python -m pip install -r requirements.txt -c outputs/torch_constraints.txt
python -m pip check
test -f .env || cp .env.example .env
```

`.env`에 기존 `report_agent_lab` DB 접속 정보, `OPENAI_API_KEY`, `LLM_MODEL`을 설정합니다. 기존 DB·저장 Vector·CUDA PyTorch 환경을 유지합니다. 새 DB 생성이나 재인덱싱은 하지 않습니다.

## 2. 오늘 구현할 Tool

| Tool | 기능 |
|---|---|
| `rag_search` | 의미 기반 검색 및 근거 기반 답변 (기존) |
| `lookup_status` | 현재 인덱싱 상태 조회 (기존) |
| `search_by_title` | 제목 Keyword 검색 (신규) |
| `get_report_detail` | 보고서 상세 정보 및 본문 Preview (신규) |
| `count_reports_by_category` | 보고서 유형별 등록 건수 집계 (신규) |

## 3. 실습 진행 순서

각 단계의 `labs/` 하위 README를 먼저 읽고, 안내된 파일의 TODO를 완성한 후 실행합니다. `__todo__(...)` 표현 전체를 필요한 코드로 교체합니다. 실습마다 새 프로젝트를 만들지 않고 동일한 프로젝트를 계속 확장합니다.

| 실습 | 강의 페이지 | 학습 내용 |
|---|---:|---|
| 01 | 7 | 기존 Day31 Agent 실행 확인 |
| 02 | 13 | Tool Schema 및 인수 검증 |
| 03 | 20 | PostgreSQL 기반 신규 Tool 3개 구현 |
| 04 | 26 | 5개 Tool 등록 및 Agent 실행 |
| 05 | 32 | 복합 업무 및 Sequential Calling |
| 06 | 38 | Middleware·Meter·호출 제한 검사 |
| 07 | 44 | FastAPI Backend 통합 |
| 08 | 50 | 전체 Agent 및 기존 RAG 기능 검증 |

아래 명령은 **각 실습의 TODO를 완료한 후 한 줄씩 순서대로** 실행합니다.

```bash
python -m tools.run_lab 01 --live --allow-paid-llm
python -m tools.run_lab 02
python -m tools.run_lab 03 --live
python -m tools.run_lab 04 --live --allow-paid-llm
python -m tools.run_lab 05 --live --allow-paid-llm
python -m tools.run_lab 06
```

`--live`는 실제 환경 실행, `--allow-paid-llm`은 비용이 발생할 수 있는 실제 LLM 호출을 허용하는 옵션입니다. 기본 보고서 ID(63), 검색어(RAG), 부재 ID(999999)는 예시이므로 실습 DB에 맞게 확인하고 필요하면 `--report-id`, `--keyword`, `--missing-id`로 변경합니다. 모든 Live 실습에서 동일한 값을 사용합니다.

## 4. 서버 실행 및 최종 검증

실습 07의 TODO를 완료한 뒤 별도 터미널에서 같은 가상환경을 활성화하고 실행합니다.

```bash
python -m app.main
```

- Swagger UI: http://127.0.0.1:8000/docs
- Health Check: `GET /health`
- Direct RAG: `POST /api/v1/rag/ask`
- Agent: `POST /api/v1/agent/ask`

기존 터미널에서 실습 07을 검증하고, 실습 08의 TODO를 완료한 뒤 다음 검증까지 수행합니다.

```bash
python -m tools.run_lab 07 --live --allow-paid-llm
python -m tools.run_lab 08 --live --allow-paid-llm
python -m pytest -q -ra
```

Postman 사용 시 `postman/agent.postman_collection.json`, `postman/local.postman_environment.json`을 Import하고 `Day32 Local`을 선택합니다. 실제 호출을 진행할 경우에만 `allow_paid_llm=true`로 설정합니다. API Key는 Postman에 입력하지 않습니다.

## 5. 완료 기준 및 주의사항

- `outputs/`에서 실제 실행 결과를 확인합니다. Fixture 테스트가 실패하거나 skip되면 Live 실행은 진행되지 않습니다.
- HTTP 200뿐 아니라 `status`, `sources`, `tool_trace`, `tool_results`를 확인합니다. 복합 업무에서는 필요한 Tool과 실제 조회 ID가 일치해야 합니다.
- `.env`, 실제 보고서 Preview와 Context를 포함한 `outputs/`는 외부에 공유하거나 Git에 올리지 않습니다.
- 구현 위치는 `docs/IMPLEMENTATION_ORDER.md`, 오류 해결은 `docs/TROUBLESHOOTING.md`를 참고합니다.

---

**코드를 단순히 완성하는 것보다, 왜 이 Tool이 선택되었고 실제 어떤 데이터가 반환되었는지 이해하는 것이 중요합니다.** 작은 단계부터 실행하고 확인하며 하나의 AI Agent 서비스를 완성해 봅시다.
