import argparse
from tools.common import check_todos
from app.services.errors import ServiceError

def main():
    p = argparse.ArgumentParser(); p.add_argument('--through',type=int,choices=range(1,9),default=8)
    p.add_argument('--part',choices=['A','B','all'],default='all'); a=p.parse_args()
    try: check_todos(a.through,a.part)
    except ServiceError: return 1
    print('지정 단계 미완성 표시 없음. 기능 검증은 별도 테스트 필요.'); return 0
if __name__=='__main__': raise SystemExit(main())
