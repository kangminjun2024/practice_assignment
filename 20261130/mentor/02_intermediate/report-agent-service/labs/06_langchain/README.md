# 실습 06. LangChain RAG Pipeline
강의 37페이지 대응 · 15분 · 02_intermediate · 강사용

## 목표
실제 LCEL invoke, Parser와 Citation 검증

## 수정 위치 및 순서
app/rag/pipeline.py, app/core/models.py, app/services/validator.py

- `D31-I06-01` · `app/rag/pipeline.py` — RunnableLambda에서 필요한 Prompt 필드 3개를 선택하고 RAG_PROMPT, model을 LCEL로 연결하세요.
- `D31-I06-02` · `app/rag/pipeline.py` — 준비된 dict를 Chain에 입력해 실제 실행하세요.
- `D31-I06-03` · `app/rag/pipeline.py` — AIMessage의 content를 기존 Parser로 검증하세요.

## 실행 (프로젝트 루트 Terminal)
```bash
python -m tools.run_lab 06
python -m tools.run_lab 06 --live --allow-paid-llm --report-id 63
```

## 완료 기준
실제 LLM 응답과 Citation, 부재 ID는 생성 호출 0회; 잘못된 JSON/출처는 Fixture로 재현

## 산출물 (`outputs/`)
rag_result.json, empty_result.json

실제 모델은 근거 부족·형식 실패를 반환할 수 있습니다. 재시도 루프를 만들지 말고 적격 보고서와 Prompt를 확인하세요. 이 실습은 API나 Agent보다 먼저 Pipeline 자체를 검증합니다.

**실제 DB에서 적격 ID를 확인하여 63을 바꿀 수 있습니다.** `--missing-id`도 실제 부재를 확인한 값으로 변경하세요. `--live` 없는 명령은 Fixture 테스트입니다. skip은 통과가 아닙니다. 이전 실습의 TODO를 유지하고 새 프로젝트를 만들지 않습니다.
