"""순차 실습 실행기. 기본은 Fixture 테스트, --live는 실제 환경. 유료 호출은 추가 동의 필요."""
import argparse
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from tools.common import ROOT, OUTPUT, save, check_todos, require, safe_error
from app.services.errors import ServiceError


def fixture_summary(report, returncode):
    # pytest는 일부 skip이 있어도 exit code 0일 수 있다. XML에서 별도로 구분한다.
    root = ET.parse(report).getroot() if report.is_file() else None
    suites = [] if root is None else ([root] if root.tag == 'testsuite' else root.findall('testsuite'))
    counts = {key:sum(int(s.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
    passed = max(0, counts['tests']-counts['failures']-counts['errors']-counts['skipped'])
    state = ('failed' if returncode not in (0,5) or counts['failures'] or counts['errors']
             else 'incomplete' if counts['skipped'] or not passed or returncode != 0 else 'passed')
    return {'mode':'fixture_tests','test_result':state,'pytest_exit_code':returncode,'passed':passed,**counts,
            'note':'Fixture 검사만을 뜻합니다. 실제 GPU·DB·LLM 연동은 별도입니다.'}


def offline(lab, part):
    files = sorted((ROOT/'tests').glob(f'test_{lab:02d}*.py'))
    if lab == 7 and part != 'all':
        files = [p for p in files if p.stem.startswith(f'test_07{part.lower()}')]
    require(bool(files), 'missing_test_file')
    print('FIXTURE / 단위 테스트: 실제 GPU·DB·LLM 성공을 의미하지 않습니다.', flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp)/'pytest.xml'
        command = [sys.executable, '-m', 'pytest', '-q', '-ra', '--junitxml', str(report), *[str(p) for p in files]]
        result = subprocess.run(command, cwd=ROOT)
        return fixture_summary(report, result.returncode)


def actual_db(args, snapshot=False):
    from app.core.settings import load_settings
    from app.core.preflight import preflight
    from app.db.connection import Database
    from app.db.repository import Repository
    from tools.check_report_db import check_ids
    settings = load_settings()
    db = Database(settings)
    try:
        repo = Repository(db)
        health = preflight(settings,repo)
        checked = check_ids(repo,args.report_id,args.missing_id)
        save('report_check.json',checked)
        require(checked['eligible'],'report_not_eligible')
        require(checked['missing_id_confirmed'],'missing_id_exists')
        if snapshot:
            path = OUTPUT/'db_before.json'
            if path.exists() and not args.reset_baseline:
                print('기존 db_before.json 보존. 새 기준이 필요할 때만 --reset-baseline을 사용하세요.')
            else:
                save('db_before.json',repo.snapshot())
        return health,checked
    finally: db.close()


def live(lab, args):
    rid=args.report_id
    q=f'보고서 {rid}번의 핵심 내용을 알려줘.'
    if lab == 1:
        from tools.check_environment import inspect_environment
        env=inspect_environment();save('environment.json',env)
        health,checked=actual_db(args,snapshot=True)
        return {'mode':'live_preflight_no_llm','health':health,'report':checked,'baseline':'outputs/db_before.json'}
    if lab == 2:
        raise ServiceError('VALIDATION_ERROR','lab02_fixture_only')
    if lab == 3:
        from app.core.runtime import Runtime
        from app.main import create_app
        from fastapi.testclient import TestClient
        created=[]
        def factory():
            runtime=Runtime();created.append(runtime);return runtime
        with TestClient(create_app(factory),raise_server_exceptions=False) as client:
            a=client.get('/health');b=client.get('/health')
            require(a.status_code==b.status_code==200,'health_failed')
            require(len(created)==1,'runtime_not_reused')
            save('health.json',a.json())
        return {'mode':'live_health_no_llm','runtime_created':len(created),'health':a.json()}
    if 4 <= lab <= 6:
        from app.core.runtime import Runtime
        from app.services.metrics import Meter
        from app.rag.documents import source_of
        actual_db(args)
        r=Runtime()
        try:
            r.health();m=Meter(r.settings)
            if lab==4:
                # Retriever 내부에서 실제 E5와 Repository가 연결된다. 검증용 벡터는 별도 1회 인코딩한다.
                vector=r.embedder.encode(q,m)
                docs=r.pipeline.retriever.search(q,None,r.settings.retrieve_k,m)
                require(len(vector)==384 and {d.metadata['report_id'] for d in docs}=={rid},'retrieval_contract')
                value={'mode':'live_cuda_db','vector_dim':len(vector),'sources':[source_of(d)|{'distance':d.metadata['distance']} for d in docs],'metrics':m.summary()}
                save('retrieval_result.json',value);return value
            if lab==5:
                # 명시 ID가 아닌 일반 의미 검색으로 여러 후보의 순위 차이를 관찰한다.
                query=args.search_query
                docs,info=r.pipeline.retrieve(query,None,r.settings.retrieve_k,m)
                context,sources=r.pipeline.build_context(docs,r.settings.context_k)
                require(bool(docs) and bool(sources),'no_context')
                require(len(context)<=r.settings.context_chars and len(sources)<=r.settings.context_k,'context_budget')
                require({x['source_id'] for x in json.loads(context)}=={s['source_id'] for s in sources},'context_sources')
                save('rerank_before.json',info['before']);save('rerank_after.json',info['after']);save('context_sources.json',sources)
                return {'mode':'live_cuda_db','before':info['before'],'after':info['after'],'included_sources':sources,'context_chars':len(context),'metrics':m.summary()}
            raw=r.pipeline.run(q,q,None,r.settings.context_k,m)
            require(raw['status']=='found' and {s['report_id'] for s in raw['sources']}=={rid},'rag_generation_not_completed')
            require(m.model_calls==1,'rag_model_attempts')
            value={'mode':'live_cuda_db_llm','result':raw,'metrics':m.summary(),'human_review':'pending'}
            save('rag_result.json',value)
            # 부재 ID로 실제 빈 후보 경로 확인: 생성 LLM 호출은 0.
            absent=f'보고서 {args.missing_id}번의 핵심 내용을 알려줘.';empty_meter=Meter(r.settings)
            empty=r.pipeline.run(absent,absent,None,r.settings.context_k,empty_meter)
            require(empty['status']=='not_found' and not empty['sources'] and empty_meter.model_calls==0,'empty_generation_not_skipped')
            save('empty_result.json',{'mode':'live_cuda_db','result':empty,'metrics':empty_meter.summary()})
            return value
        finally:r.close()
    # 실습 07/08은 실제 localhost Uvicorn으로 HTTP 요청. 테스트용 TestClient가 아니다.
    import httpx
    health,checked=actual_db(args)
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    from app.schemas.rag import RagAskResponse
    from app.schemas.agent import AskResponse
    base_url=f'http://127.0.0.1:{args.port}'
    checks={}
    with httpx.Client(base_url=base_url,timeout=args.http_timeout,trust_env=False) as client:
        spec=client.get('/openapi.json');require(spec.status_code==200 and spec.json().get('info',{}).get('title')=='Day31 Report Agent Service','wrong_server')
        h=client.get('/health');require(h.status_code==200 and h.json().get('database')=='report_agent_lab' and h.json().get('gpu')=='cuda:0','server_health')
        def post(path,question):
            return client.post(path,json={'question':question,'category_code':None})
        rag='/api/v1/rag/ask';agent='/api/v1/agent/ask'
        status_q=f'보고서 {rid}번의 현재 인덱싱 상태를 알려줘.'
        both_q=f'보고서 {rid}번의 핵심 내용과 현재 인덱싱 상태를 알려줘.'
        def simple(label,response,cls):
            require(response.status_code==200,label+'_http')
            out=cls.model_validate(response.json());require(out.status=='completed',label+'_not_completed')
            checks[label]=out.model_dump();return out
        if lab==7:
            if args.part in ('A','all'):
                result=simple('direct_rag',post(rag,q),RagAskResponse)
                require(len(result.sources)==1 and result.sources[0].report_id==rid,'direct_rag_wrong_source')
                from tools.acceptance import validate_citation_contract
                validate_citation_contract(result)
            if args.part in ('B','all'):
                # 실제 2개 Tool이 모두 연결됐는지 한 복합 요청으로 확인한다.
                result=simple('agent_both',post(agent,both_q),AskResponse)
                from tools.acceptance import validate_citation_contract
                validate_citation_contract(result)
                for name in ('rag_search','lookup_status'):
                    require(any(t.tool==name and t.status=='found' for t in result.tool_trace),'missing_successful_'+name)
                require(result.validation.required_tools_observed and result.validation.citations_match_context,'agent_validation')
                require(len(result.sources)==1 and result.sources[0].report_id==rid,'agent_wrong_source')
                state=checked['lookup_status']
                expected_line=f"보고서 {rid}: index_status={state['index_status']}, revision={state['revision']}, embedding_fresh={str(state['embedding_fresh']).lower()}"
                require(expected_line in result.answer.splitlines(),'agent_db_status')
            return {'mode':'live_http','checks':checks,'note':'07-A의 출처·07-B의 두 Tool 및 DB 상태를 검사. 실습 08에서 개별/복합 Task와 실패 경로를 검증. 서버 Meter 로그도 확인.'}
        from tools.acceptance import validate_rag,validate_agent,validate_empty,validate_snapshot
        baseline=OUTPUT/'db_before.json'
        require(baseline.is_file(),'db_baseline_missing_run_lab01')
        before=json.loads(baseline.read_text(encoding='utf-8'))
        db=Database(load_settings())
        try:
            repo=Repository(db)
            expected=repo.lookup(rid)
            require(expected['status']=='found','report_disappeared')
            checks['direct_rag']=validate_rag(post(rag,q),rid)
            checks['direct_empty']=validate_empty(post(rag,f'보고서 {args.missing_id}번의 핵심 내용을 알려줘.'))
            bad=post(rag,'ab');require(bad.status_code==422 and bad.json()['error']['code']=='VALIDATION_ERROR','schema_422')
            checks['invalid_schema']={'http_status':bad.status_code,'body':bad.json()}
            bad_id=post(agent,'보고서 0번의 내용을 알려줘.');require(bad_id.status_code==422,'invalid_report_id')
            checks['invalid_id']={'http_status':bad_id.status_code,'body':bad_id.json()}
            checks['agent_rag']=validate_agent(post(agent,q),{'rag_search'},rid)
            checks['agent_status']=validate_agent(post(agent,status_q),{'lookup_status'},rid,expected)
            checks['agent_both']=validate_agent(post(agent,both_q),{'rag_search','lookup_status'},rid,expected)
            after=repo.snapshot();save('db_after.json',after)
            checks['db_unchanged']=validate_snapshot(before,after)
        finally:
            # 실패한 단계 이전의 증거도 보존한다. 실패를 성공으로 기록하지 않는다.
            save('verification_partial.json',{'mode':'live_http_attempt','checks':checks,'human_review':'pending'})
            db.close()
    return {'mode':'live_http','checks':checks,'human_review':'pending','note':'출처·Tool Trace·DB 값 구조 검사 통과 여부. 내용 Faithfulness 및 서버 로그의 호출 수는 별도 사람 검토.'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('lab',type=int,choices=range(1,9));p.add_argument('--live',action='store_true')
    p.add_argument('--allow-paid-llm',action='store_true');p.add_argument('--part',choices=['A','B','all'],default='all')
    p.add_argument('--report-id',type=int,default=63);p.add_argument('--missing-id',type=int,default=999999)
    p.add_argument('--search-query',default='RAG 검색 품질 향상을 위한 연구 내용을 찾아줘.')
    p.add_argument('--port',type=int,default=8000);p.add_argument('--http-timeout',type=float,default=300)
    p.add_argument('--reset-baseline',action='store_true');args=p.parse_args(argv)
    name=f'lab_{args.lab:02d}'+(f'_{args.part}' if args.lab==7 else '')+('_live' if args.live else '_fixture')+'.json'
    try:
        if args.live and args.lab>=6 and not args.allow_paid_llm:
            raise ServiceError('VALIDATION_ERROR','paid_llm_requires_explicit_flag')
        check_todos(args.lab,args.part)
        result=live(args.lab,args) if args.live else offline(args.lab,args.part)
        if not args.live and result['test_result'] != 'passed':
            save(name,{'execution':result['test_result'],'result':result})
            print('Fixture 검사 미완료 또는 실패:',result['test_result'],'skip:',result['skipped'])
            return 1
        save(name,{'execution':'checks_completed','result':result});print('단계 검사 완료. 실제 실행과 Fixture 결과를 구분하세요.');return 0
    except Exception as exc:
        err=safe_error(exc);save(name,{'execution':'failed','error':err});print(err);return 1
if __name__=='__main__':raise SystemExit(main())
