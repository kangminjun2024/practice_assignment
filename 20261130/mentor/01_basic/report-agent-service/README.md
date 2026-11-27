# DAY31 · FastAPI & LangChain Integration
**01_basic / 강사용 정답 및 해설** · 2026-11-30

## 최종 목표
하나의 report-agent-service에서 Direct RAG API와 LangChain `create_agent()` 기반 Agent API를 완성합니다. 기존 Day30의 CUDA E5, Cross-Encoder, PostgreSQL/pgvector, 2개 읽기 전용 Tool을 재사용합니다. Day32에 Tool 3개를 확장할 예정입니다. LangGraph/MCP/Frontend를 직접 구현하지 않습니다.

## 1. 시작
VS Code로 **이 report-agent-service 폴더 하나만** 엽니다. 기존 CUDA venv의 Python Interpreter를 선택하고 Git Bash Terminal을 엽니다. `which python`, `python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"`로 확인합니다. 기존 환경을 복제하거나 PyTorch를 강제 재설치하지 마세요.
```bash
python -m tools.preserve_torch
python -m pip install -r requirements.txt -c outputs/torch_constraints.txt
python -m pip check
test -f .env || cp .env.example .env
```
이미 `.env`가 있으면 덮어쓰지 말고 기존 DB URL/API Key/Tool Calling 가능한 Model ID를 사용합니다. 기존 환경변수가 .env보다 우선합니다. DB는 기존 `report_agent_lab`입니다. `.env`·실제 응답·로그를 Git에 올리지 않습니다. 실제 LLM에 보고서 Context가 전송되므로 교육용 데이터만 사용합니다.
```bash
python -m tools.check_environment
python -m tools.check_report_db --report-id 63 --missing-id 999999
python -m tools.run_lab 01 --live --report-id 63 --missing-id 999999
```
63번은 예시일 뿐입니다. 적격 ID가 없으면 기존 DB/Vector를 담당 강사와 확인합니다. 자동 Reindexing, DB 생성, CPU 대체는 하지 않습니다. 선택한 부재 ID도 반드시 존재하지 않는 양의 ID여야 합니다.

## 2. 순차 실습
| 실습 | 페이지 | 주제 | TODO | 시간 | 안내 |
|---|---:|---|---:|---:|---|
| 01 | 7 | Project Setup | 0 | 10분 | `01_project_setup` |
| 02 | 13 | FastAPI & API Contract | 2 | 10분 | `02_api_contract` |
| 03 | 19 | Configuration & Runtime | 2 | 10분 | `03_runtime` |
| 04 | 25 | Repository & Retriever | 2 | 15분 | `04_retriever` |
| 05 | 31 | Reranking & Context | 2 | 15분 | `05_context` |
| 06 | 37 | LangChain RAG Pipeline | 2 | 15분 | `06_langchain` |
| 07 | 43 | Backend & Agent Integration | 4 | 25분 | `07_integration` |
| 08 | 50 | API Testing & Debugging | 2 | 20분 | `08_verification` |

실제 TODO는 `app/` 또는 `tools/acceptance.py`에 있습니다. `labs/`에는 단계별 README, Expected, Review, 실행기만 있습니다. 이전 실습에서 수정한 프로젝트를 그대로 사용하세요. `# BEGIN/END` 사이의 미완성 코드만 실제 구현으로 교체합니다. 미완성 `UNIMPLEMENTED_...`를 제거하되 단순히 제거하는 것만으로 정답이 되지는 않습니다. 테스트를 통과해야 합니다. `docs/todo_map.json`은 위치/힌트만 포함합니다.

- 실습별 검증: `python -m tools.run_lab 02` 등. `--live`가 없으면 Fixture 기반 pytest입니다.
- 실습 01·03~05 실제 점검: `--live --report-id 63`.
- 실습 06~08 실제 점검: `--live --allow-paid-llm --report-id 63`.
- 실습 07: `--part A` 후 `--part B`. A의 검사에서는 B의 TODO를 요구하지 않습니다.
- 전체 검증: 모든 TODO 완료 후 `python -m pytest -q -ra`. SDK 미설치로 skip한 경우 실행 성공으로 보지 않습니다. 단계 실행기도 skip을 미완료로 저장하고 종료 코드 1을 반환합니다.

## 3. 실제 서버 실행 (07-A 이후)
```bash
python -m tools.check_todos --through 7 --part A
python -m app.main
```
또는 `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.
다른 Terminal/Swagger/Postman에서 테스트합니다. 수정 후 서버를 재시작하세요. 07-B 미완성 중에는 Agent API를 호출하지 않습니다. 실제 API 호출은 유료 LLM 호출을 발생시킬 수 있습니다. 실행기의 `--allow-paid-llm`은 CLI에만 적용되며, Swagger/Postman 직접 요청에는 별도 플래그가 없습니다.

| Method | URL | 기능 |
|---|---|---|
| GET | http://127.0.0.1:8000/health | Preflight (실제 추론 검증 아님) |
| POST | http://127.0.0.1:8000/api/v1/rag/ask | Direct RAG |
| POST | http://127.0.0.1:8000/api/v1/agent/ask | 실제 Agent + 2 Tool |
| GET | http://127.0.0.1:8000/docs | Swagger UI |

```json
{"question":"보고서 63번의 핵심 내용을 알려줘.","category_code":null}
```

## 4. 검증과 한계
`completed`는 구조 계약 및 Tool/출처 검사 결과이며 의미적 Faithfulness를 보장하지 않습니다. 실제 보고서 원문과 답변을 사람도 확인합니다. 정확한 LLM 호출 순서 및 자연어 문장을 고정하지 않습니다. 실패한 실행을 `completed`로 대체하지 않습니다. 모든 자료는 로컬 교육용 단일 Worker 서비스입니다(인증·사용자 격리·운영 수준 로그 정책은 별도). DB는 읽기 전용 코드이지만 실제 DB Role도 최소 권한이어야 합니다.

`docs/IMPLEMENTATION_ORDER.md`, `docs/TROUBLESHOOTING.md`, `docs/SOURCE_ALIGNMENT.md`, `postman/POSTMAN_GUIDE.md` 참조. 강의자료 43p 이후 07-B는 승인된 확장 실습이며 오전 120분 안에 부담되면 오후 개인 실습 시간에 이어서 진행합니다.

## 재검수 보완 사항
`tools.preserve_torch`로 현재 설치된 torch/torchvision/torchaudio 버전을 고정합니다. 충돌하면 CUDA 패키지를 업그레이드하지 말고 강사와 호환 범위를 확인합니다. 07-B Live는 복합 요청 한 번으로 두 Tool을 검증합니다. `category_code`는 기존 계약대로 RAG 검색 범위이며 `lookup_status`는 명시 ID 기반 조회입니다. 이것은 사용자 권한 필터가 아닙니다.
