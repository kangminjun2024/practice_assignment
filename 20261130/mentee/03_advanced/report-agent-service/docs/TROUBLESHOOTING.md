# Troubleshooting · Windows 11 / VS Code / Git Bash
| 현상 | 확인 | 대응 |
|---|---|---|
| ModuleNotFoundError | `which python`, `python -m pip check` | VS Code Interpreter를 기존 CUDA venv로 선택, requirements 설치. torch 강제 재설치 금지 |
| GPU_UNAVAILABLE | `nvidia-smi`, `python -c "import torch; print(torch.cuda.is_available())"` | 기존 CUDA 지원 PyTorch/Driver 확인. CPU 전환 금지 |
| DB_UNAVAILABLE | .env URL, pgAdmin의 report_agent_lab, pgvector, 6종 Category, report_read_view | 기존 DB 이름 및 비밀번호/권한 확인. 생성/DDL 실행 금지 |
| EMBEDDING_UNAVAILABLE | /health 적격 수, check_report_db | 0이면 기존 인덱스 상태, revision/hash/model 확인. 다른 적격 ID 선택. 전체 Reindexing은 하지 않는다 |
| LLM_UNAVAILABLE | 설정/인증/Rate Limit, 안전한 reason | API Key와 Model ID/Tool Calling 지원 여부 확인. 키를 출력하지 않는다. .env보다 OS 환경변수 우선 |
| LLM_TIMEOUT | 공급자 응답 지연, 첫 모델 로딩 | 서버 로그에서 구간 분리. 임의 반복 호출 금지 |
| OUTPUT_CONTRACT_ERROR | JSON/Source ID/Candidate 계약 | 실제 Context의 ID와 모델 출력 확인. 고정 답변 반환 금지 |
| NOT_IMPLEMENTED | TODO ID/실습 순서 | `python -m tools.check_todos --through 7 --part A` 등으로 위치 확인 |
| 404 / 405 | URL, Method, Router 등록, 서버 포트 | `/docs` 확인. 수정 후 Uvicorn 재시작 |
| 422 | 필드·길이·Category·명시 ID | body JSON 확인. query/k 등 허용되지 않는 필드 제거 |
| HTTP 연결 실패 | 서버 Terminal 및 포트 | 동일 프로젝트 서버가 떠 있는지 확인, --port 지정 |
| DB Snapshot 불일치 | 외부 데이터 변경 여부 | 자동 합격 처리하지 않음. 강사와 변경 원인을 확인하고 필요할 때만 --reset-baseline |
| `sdk_import_failed` | 패키지는 설치됐으나 SDK import 실패 | `python -m pip check`, 기존 CUDA venv·torch 버전·SDK 호환성을 확인. 실제 모델을 CPU로 전환하지 않음 |

LLM SDK 원본 예외·보고서 내용·API Key를 공개 채널에 복사하지 않는다. 테스트용 Fixture와 실제 호출을 구분한다. API 인증/운영 권한은 이 로컬 실습 범위를 벗어난다.

Fixture 결과 `execution: incomplete`는 skip 또는 테스트 미수집입니다. 설치·TODO를 점검한 뒤 재실행하세요.
