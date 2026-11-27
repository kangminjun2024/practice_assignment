import re
from app.services.errors import ServiceError


def explicit_ids(query):
    # 지원하는 명시 ID 표기만 추출한다. 범위 밖 ID를 무시하지 않는다.
    matches = re.findall(
        r'(?:보고서\s*(?:번호\s*)?#?\s*|RPT-|report\s*(?:id\s*)?#?\s*)([+-]?[0-9]+)',
        query, re.I,
    )
    ids = set()
    for value in matches:
        try:
            report_id = int(value)
        except ValueError:
            raise ServiceError('VALIDATION_ERROR', 'invalid_report_id') from None
        # BEGIN D31-A04-04
        # 해설 D31-A04-04: 범위 밖 명시 ID를 삭제하면 의도하지 않은 일반 검색이 실행될 수 있다.
        if not 1 <= report_id <= 9223372036854775807:
            raise ServiceError('VALIDATION_ERROR', 'invalid_report_id')
        # END D31-A04-04
        ids.add(report_id)
    return ids
