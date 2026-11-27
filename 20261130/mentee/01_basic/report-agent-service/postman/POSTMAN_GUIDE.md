# Postman 검증 안내
1. `python -m app.main` 실행. 서버 수정 시 재시작.
2. Collection과 Environment JSON 파일을 Import한 뒤 Day31 Local 환경을 선택한다.
3. `report_id`, `missing_id`를 실제 확인한 양의 ID로 변경한다. `base_url`은 로컬 주소.
4. Health와 Input 422는 비용 없이 실행한다. Direct RAG Empty는 실제 GPU/DB를 사용하며 확인된 부재 ID일 때 생성 LLM을 생략한다.
5. RAG/Agent 요청(Empty 포함)을 보내려면 Environment의 `allow_paid_llm`을 `true`로 설정한다. 부재 ID가 실제로 존재하게 되면 Empty 요청도 유료 호출을 할 수 있다. 실행 전 각 요청의 Body를 확인한다. Agent 3개 Task는 실제 모델 선택을 사용하며 정확한 호출 순서를 검사하지 않는다.
6. Collection 테스트는 HTTP/구조 및 Tool Trace를 확인한다. 실제 DB 값·불변성·사실성은 `tools.run_lab 08 --live --allow-paid-llm`과 원문 사람 검토로 확인한다.

비용이 발생할 수 있으므로 Collection 전체 반복 실행은 피한다. API Key를 Postman에 넣지 않는다. 출처 실패는 `python -m tools.run_lab 06`의 결정적 Fixture 테스트에서 확인한다. Collection 및 CLI는 동시에 여러 요청을 보내지 않는다.
