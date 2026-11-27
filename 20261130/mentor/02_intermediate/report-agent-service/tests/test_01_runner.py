"""실습 실행기의 테스트 집계와 CUDA 설치 버전 보호 계약."""
import json
import pytest
from tools import run_lab
from tools import preserve_torch

@pytest.mark.parametrize('code,tests,failed,errors,skipped,state',[
    (0,2,0,0,0,'passed'), (0,2,0,0,1,'incomplete'),
    (5,1,0,0,1,'incomplete'), (5,0,0,0,0,'incomplete'),
    (1,2,1,0,0,'failed'), (2,1,0,1,0,'failed'),
])
def test_fixture_summary(tmp_path,code,tests,failed,errors,skipped,state):
    report=tmp_path/'pytest.xml'
    report.write_text(f'<testsuites><testsuite tests="{tests}" failures="{failed}" errors="{errors}" skipped="{skipped}" /></testsuites>')
    out=run_lab.fixture_summary(report,code)
    assert out['test_result']==state and out['passed']==tests-failed-errors-skipped


def test_runner_skip_is_not_complete(monkeypatch):
    saved={}
    monkeypatch.setattr(run_lab,'check_todos',lambda *args:None)
    monkeypatch.setattr(run_lab,'offline',lambda *args:{'test_result':'incomplete','skipped':1})
    monkeypatch.setattr(run_lab,'save',lambda name,value:saved.update(value))
    assert run_lab.main(['01'])==1 and saved['execution']=='incomplete'


def test_preserve_cuda_versions(monkeypatch,tmp_path):
    versions={'torch':'2.7.1+cu118','torchvision':'0.22.1+cu118'}
    def get_version(name):
        if name not in versions:raise preserve_torch.PackageNotFoundError(name)
        return versions[name]
    monkeypatch.setattr(preserve_torch,'ROOT',tmp_path)
    monkeypatch.setattr(preserve_torch,'version',get_version)
    assert preserve_torch.main()==0
    assert (tmp_path/'outputs/torch_constraints.txt').read_text().splitlines()==['torch===2.7.1+cu118','torchvision===0.22.1+cu118']
