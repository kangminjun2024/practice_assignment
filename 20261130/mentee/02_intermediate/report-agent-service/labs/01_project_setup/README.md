# 실습 01. Project Setup
강의 7페이지 대응 · 10분 · 02_intermediate · 수강생용

## 목표
기존 환경 확인, DB 적격 보고서/부재 ID 확인, 불변성 기준 확보

## 수정 위치 및 순서
tools/check_environment.py, tools/check_report_db.py, app/core/settings.py, app/db/repository.py

환경 준비 단계입니다. 코드 TODO가 없습니다.

## 실행 (프로젝트 루트 Terminal)
```bash
python -m tools.run_lab 01
python -m tools.run_lab 01 --live --report-id 63
```

## 완료 기준
실제 CUDA/DB/설정 검사; GPU 모델 및 LLM 추론은 아직 실행하지 않음

## 산출물 (`outputs/`)
environment.json, report_check.json, db_before.json

실제 환경을 처음 확인할 때 기존 `outputs/db_before.json`을 저장합니다. 다른 사람의 DB 변경을 중단한 상태에서 비교하세요. 부재 ID 기본값 999999는 실제 존재하지 않는지 확인 후 사용합니다.

**실제 DB에서 적격 ID를 확인하여 63을 바꿀 수 있습니다.** `--missing-id`도 실제 부재를 확인한 값으로 변경하세요. `--live` 없는 명령은 Fixture 테스트입니다. skip은 통과가 아닙니다. 이전 실습의 TODO를 유지하고 새 프로젝트를 만들지 않습니다.

패키지를 설치하기 전 루트 README의 `tools.preserve_torch`를 실행하고 `-c outputs/torch_constraints.txt`를 사용하세요. 현재 CUDA 패키지 버전과 충돌하면 기존 CUDA 환경을 유지한 채 강사와 확인합니다.
