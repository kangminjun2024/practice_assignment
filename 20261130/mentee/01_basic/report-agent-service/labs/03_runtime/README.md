# 실습 03. Configuration & Runtime
강의 19페이지 대응 · 10분 · 01_basic · 수강생용

## 목표
Runtime에서 의존 객체를 조립하고 동일 Application에서 재사용

## 수정 위치 및 순서
app/core/runtime.py, app/main.py, app/core/preflight.py

- `D31-B03-01` · `app/core/runtime.py` — Settings와 준비한 Pipeline으로 RagService를 생성하세요.
- `D31-B03-02` · `app/core/runtime.py` — 기존 preflight 함수로 Settings와 Repository의 준비 상태를 반환하세요.

## 실행 (프로젝트 루트 Terminal)
```bash
python -m tools.run_lab 03
python -m tools.run_lab 03 --live --report-id 63
```

## 완료 기준
동일 Runtime 생성 1회, 종료 시 close; 실제 /health 200은 LLM 인증/추론 성공 아님

## 산출물 (`outputs/`)
health.json, lab_03_live.json

CUDA 모델 객체는 Lazy Loading이므로 Health Check에서 모델 추론을 실행하지 않습니다.

**실제 DB에서 적격 ID를 확인하여 63을 바꿀 수 있습니다.** `--missing-id`도 실제 부재를 확인한 값으로 변경하세요. `--live` 없는 명령은 Fixture 테스트입니다. skip은 통과가 아닙니다. 이전 실습의 TODO를 유지하고 새 프로젝트를 만들지 않습니다.
