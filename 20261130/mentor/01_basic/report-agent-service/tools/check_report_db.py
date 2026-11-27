"""기존 보고서 적격성과 부재 ID를 실제 읽기 전용 SELECT로 확인."""
import argparse
from sqlalchemy import text
from app.core.settings import load_settings, MODEL
from app.db.connection import Database
from app.db.repository import Repository, JOIN, FRESH
from app.schemas.agent import ReportId
from pydantic import TypeAdapter
from tools.common import require, save, safe_error

def check_ids(repo, report_id, missing_id=999999):
    report_id = TypeAdapter(ReportId).validate_python(report_id)
    missing_id = TypeAdapter(ReportId).validate_python(missing_id)
    state = repo.lookup(report_id)
    with repo.db.read() as conn:
        eligible = bool(conn.execute(text('SELECT EXISTS (SELECT 1 '+JOIN+' WHERE '+FRESH+' AND r.report_id=:rid)'),
                                     {'model':MODEL,'rid':report_id}).scalar_one())
        alternatives = list(conn.execute(text('SELECT DISTINCT r.report_id '+JOIN+' WHERE '+FRESH+' ORDER BY r.report_id LIMIT 12'),
                                         {'model':MODEL}).scalars())
        missing = not bool(conn.execute(text('SELECT EXISTS (SELECT 1 FROM public.reports WHERE report_id=:rid)'),
                                        {'rid':missing_id}).scalar_one())
    return {'report_id':report_id,'exists':state['status']=='found','eligible':eligible,
            'lookup_status':state,'eligible_id_examples':alternatives,'missing_id':missing_id,'missing_id_confirmed':missing}

def main():
    p=argparse.ArgumentParser();p.add_argument('--report-id',type=int,default=63);p.add_argument('--missing-id',type=int,default=999999);a=p.parse_args()
    db=None
    try:
        db=Database(load_settings()); out=check_ids(Repository(db),a.report_id,a.missing_id); save('report_check.json',out);print(out)
        if not out['eligible'] or not out['missing_id_confirmed']:
            print('적격 ID 예시를 확인하고 실제 부재하는 양의 ID로 다시 실행하세요.');return 1
        return 0
    except Exception as exc: print(safe_error(exc)); return 1
    finally:
        if db is not None:db.close()
if __name__=='__main__':raise SystemExit(main())
