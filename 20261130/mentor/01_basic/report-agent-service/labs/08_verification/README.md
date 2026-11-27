# 실습 08. API Testing & Debugging
강의 50페이지 대응 · 20분 · 01_basic · 강사용

## 목표
전체 HTTP/Tool/DB 계약 및 실패 경로 검증

## 수정 위치 및 순서
tools/acceptance.py, tests/test_08*.py

- `D31-B08-01` · `tools/acceptance.py` — 응답 완료 상태와 실제 요청 보고서 ID 집합을 검사하세요.
- `D31-B08-02` · `tools/acceptance.py` — Agent 완료 상태, 필요한 found Tool 포함 여부, 실행 검증 Flag를 확인하세요.

## 실행 (프로젝트 루트 Terminal)
```bash
python -m tools.run_lab 08
python -m tools.run_lab 08 --live --allow-paid-llm --report-id 63
```

## 완료 기준
정상 RAG, 유효 후보 없음, 422, 잘못된 Citation(Fixture), 3개 실제 Agent Task, DB 불변성

## 산출물 (`outputs/`)
lab_08_live.json, verification_partial.json, db_after.json

실제 서버를 실행한 상태에서 별도 Terminal로 검증합니다. Citation 실패와 호출 상한은 결정적 Fixture 테스트로 재현합니다. DB 비교 전에 외부 서비스의 변경이 없어야 하며, 사람 검토가 필요합니다.

**실제 DB에서 적격 ID를 확인하여 63을 바꿀 수 있습니다.** `--missing-id`도 실제 부재를 확인한 값으로 변경하세요. `--live` 없는 명령은 Fixture 테스트입니다. skip은 통과가 아닙니다. 이전 실습의 TODO를 유지하고 새 프로젝트를 만들지 않습니다.
