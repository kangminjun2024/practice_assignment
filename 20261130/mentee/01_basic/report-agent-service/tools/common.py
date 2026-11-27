"""로컬 산출물 및 단계별 미완성 TODO 검사."""
from pathlib import Path
import json
import re
from app.services.errors import ServiceError

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'outputs'

def save(name, value):
    path = OUTPUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    print('저장:', path.relative_to(ROOT))
    return path

def require(condition, reason):
    if not condition:
        raise ServiceError('OUTPUT_CONTRACT_ERROR', reason)

def check_todos(through, part='all'):
    # 정답을 갖고 있지 않다. 단계별 미완성 표시만 검사한다.
    manifest = json.loads((ROOT/'docs'/'todo_map.json').read_text(encoding='utf-8'))
    pending = []
    for task in manifest:
        if task['lab'] > through or (through == 7 and part == 'A' and task['lab'] == 7 and task['part'] == 'B'):
            continue
        text = (ROOT/task['file']).read_text(encoding='utf-8')
        if 'UNIMPLEMENTED_'+task['id'] in text:
            pending.append(task['id']+' · '+task['file'])
    if pending:
        print('먼저 다음 TODO를 완성하세요:\n'+'\n'.join(pending))
        raise ServiceError('NOT_IMPLEMENTED','pending_lab_todos')

def safe_error(exc):
    if isinstance(exc, ServiceError):
        return exc.envelope()
    # 원본 예외와 DB URL/키/본문은 외부 출력에 포함하지 않는다.
    return {'error': {'code': 'LOCAL_EXECUTION_ERROR', 'type': type(exc).__name__}}
