# 실습 04. Repository & Retriever
강의 25페이지 대응 · 15분 · 02_intermediate · 강사용

## 목표
질문→CUDA E5→pgvector SQL→Document

## 수정 위치 및 순서
app/rag/retriever.py, app/db/repository.py, app/rag/embeddings.py, app/rag/documents.py, app/rag/ids.py

- `D31-I04-01` · `app/rag/retriever.py` — 현재 질문과 Meter를 사용해 E5 인코딩을 호출하세요.
- `D31-I04-02` · `app/rag/retriever.py` — Repository 후보 조회 결과를 rows에 추가하세요.
- `D31-I04-03` · `app/rag/retriever.py` — 거리 오름차순·ID 동점 기준으로 최대 top_k개를 정렬하고 Document로 반환하세요.

## 실행 (프로젝트 루트 Terminal)
```bash
python -m tools.run_lab 04
python -m tools.run_lab 04 --live --report-id 63
```

## 완료 기준
Vector 384차원, 명시 ID 조건 및 Metadata 보존

## 산출물 (`outputs/`)
retrieval_result.json

검증 목적으로 Vector를 한 번 별도 인코딩한 뒤 Retriever가 다시 인코딩합니다. 서비스 요청에서 E5를 불필요하게 두 번 실행하는 구조는 아닙니다.

**실제 DB에서 적격 ID를 확인하여 63을 바꿀 수 있습니다.** `--missing-id`도 실제 부재를 확인한 값으로 변경하세요. `--live` 없는 명령은 Fixture 테스트입니다. skip은 통과가 아닙니다. 이전 실습의 TODO를 유지하고 새 프로젝트를 만들지 않습니다.
