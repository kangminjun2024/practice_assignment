# 실습 05. Reranking & Context
강의 31페이지 대응 · 15분 · 02_intermediate · 수강생용

## 목표
같은 후보 Reranking 및 Context 구성

## 수정 위치 및 순서
app/rag/reranker.py, app/rag/pipeline.py

- `D31-I05-01` · `app/rag/pipeline.py` — 현재 질문과 후보 목록으로 Reranker를 호출하세요.
- `D31-I05-02` · `app/rag/pipeline.py` — 길이 검사를 통과한 item과 해당 Document의 Source를 각각 추가하세요.
- `D31-I05-03` · `app/rag/pipeline.py` — Source Metadata와 본문을 합치고 본문을 문서당 3000자 및 remaining 이내로 제한하세요.

## 실행 (프로젝트 루트 Terminal)
```bash
python -m tools.run_lab 05
python -m tools.run_lab 05 --live --report-id 63
```

## 완료 기준
동일 후보 집합·점수·Context 길이 예산·실제 포함 Source ID

## 산출물 (`outputs/`)
rerank_before.json, rerank_after.json, context_sources.json

일반 검색 질문으로 후보 순위 차이를 관찰합니다. 후보가 하나뿐이거나 순위가 동일해도 오류는 아닙니다. JSON 길이 제한은 Token 제한이 아닙니다.

**실제 DB에서 적격 ID를 확인하여 63을 바꿀 수 있습니다.** `--missing-id`도 실제 부재를 확인한 값으로 변경하세요. `--live` 없는 명령은 Fixture 테스트입니다. skip은 통과가 아닙니다. 이전 실습의 TODO를 유지하고 새 프로젝트를 만들지 않습니다.
