"""설치되어 있는 CUDA PyTorch 계열 버전을 constraints로 보존합니다."""
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    lines=[]
    for name in ('torch','torchvision','torchaudio'):
        try:
            lines.append(f'{name}==={version(name)}')
        except PackageNotFoundError:
            if name=='torch':
                print('기존 CUDA 가상환경을 먼저 활성화하세요. torch가 없습니다.')
                return 1
    out=ROOT/'outputs'/'torch_constraints.txt'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('기존 설치 버전 고정:',out.relative_to(ROOT))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
