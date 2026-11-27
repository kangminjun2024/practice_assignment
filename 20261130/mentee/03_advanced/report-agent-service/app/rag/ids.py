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
        # TODO D31-A04-04: report_id가 양의 PostgreSQL bigint 범위를 벗어나면 VALIDATION_ERROR를 발생시키세요.
        raise ServiceError('NOT_IMPLEMENTED', 'UNIMPLEMENTED_D31-A04-04')
        # END D31-A04-04
        ids.add(report_id)
    return ids
