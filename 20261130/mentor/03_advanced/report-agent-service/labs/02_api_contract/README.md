# 실습 02. FastAPI & API Contract
강의 13페이지 대응 · 10분 · 03_advanced · 강사용

## 목표
Request/Response Schema와 Router 등록을 연결

## 수정 위치 및 순서
app/schemas/rag.py, app/api/rag.py, app/main.py

- `D31-A02-01` · `app/schemas/rag.py` — question에 위에서 선언한 검증 타입을 지정하세요.
- `D31-A02-02` · `app/main.py` — FastAPI app에 RAG Router를 등록하세요.
- `D31-A02-03` · `app/api/rag.py` — RAG 응답 모델을 route의 response_model에 연결하세요.
- `D31-A02-04` · `app/main.py` — 요청 검증 오류를 지정한 HTTP 상태 및 공통 Error Envelope로 반환하세요.

## 실행 (프로젝트 루트 Terminal)
```bash
python -m tools.run_lab 02
```

## 완료 기준
TestClient 200·422·404·405 및 응답 Schema 오류 확인. Stub 응답으로만 HTTP 계약 검증

## 산출물 (`outputs/`)
lab_02_fixture.json (pytest 실행 상태)

실습 07의 RAG 업무 구현은 아직 미완성입니다. 이 단계에서는 실제 서비스 호출 대신 TestClient Stub을 사용합니다.

**실제 DB에서 적격 ID를 확인하여 63을 바꿀 수 있습니다.** `--missing-id`도 실제 부재를 확인한 값으로 변경하세요. `--live` 없는 명령은 Fixture 테스트입니다. skip은 통과가 아닙니다. 이전 실습의 TODO를 유지하고 새 프로젝트를 만들지 않습니다.
