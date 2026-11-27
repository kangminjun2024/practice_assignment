"""프로젝트 내 실제 모듈을 검증한다. 별도의 완성 코드를 갖지 않는다."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.run_lab import main
if __name__ == '__main__':
    raise SystemExit(main(['01', *sys.argv[1:]]))
