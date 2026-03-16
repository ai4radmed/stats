# sync_performance.py 명세

## 1. 개요
식약처의 "의약품등 생산수입실적조회" API를 사용하여 방사성의약품의 연도별 실적 데이터를 수집하고 Supabase의 `mfds_item_performance` 테이블에 저장합니다.

## 2. API 정보
- **서비스명**: 의약품등 생산수입실적 정보 서비스
- **엔드포인트**: `https://apis.data.go.kr/1471000/MdcinPrdctnImportAcmsltService02/getMdcinPrdctnImportrstList02`
- **주요 요청 파라미터**:
    - `serviceKey`: 인증키 (디코딩된 키 권장)
    - `type`: `json`
    - `date_year`: 대상 연도 (예: 2023, 2024)
    - `item_name`: 제품명 (선택 사항이나, 특정 제품 수집 시 유용)

## 3. 핵심 로직 흐름
1.  **대상 확인**: Supabase의 `mfds_radpharm_master` 테이블에서 현재 관리 중인 모든 `item_name` 리스트를 조회합니다.
2.  **API 호출 전략 (품목별 검색)**: 
    - 수만 건의 일반 의약품 데이터를 피하기 위해, 수집된 각 `item_name`을 API의 검색 인자로 전달합니다. (`&item_name={item_name}`)
    - 대상 연도(`date_year`)와 품목명을 조합하여 정밀하게 조회합니다.
3.  **데이터 파싱**:
    - API 응답의 `body -> items -> [ { "item": { ... } } ]` 구조를 올바르게 처리합니다.
    - `AMT` 필드를 정수형으로 변환합니다.
4.  **DB 저장 (Upsert)**:
    - `item_seq`, `year`, `result_part`를 고유 키로 하여 `upsert`를 수행합니다.
5.  **로그 기록**: `api_sync_log`에 수집 결과를 기록합니다.

## 4. 핵심 비즈니스 규칙 및 데이터 연결
- **핵심 연결 키 (item_seq)**: API 응답의 `ITEM_SEQ`(품목기준코드)를 실적 테이블의 `item_seq`로 저장하며, 이는 `mfds_radpharm_master` 테이블의 기본키와 1:1로 대응됩니다.
- **중복 방지**: 한 품목(`item_seq`)에 대해 동일한 연도(`year`)와 동일한 실적 구분(`result_part`)을 가진 데이터는 하나만 존재해야 합니다. (DB의 Unique 제약 조건 활용)
- **예외 처리**: 
    - API 호출 실패 시 로그를 남기고 다음 연도로 넘어갑니다.
    - `item_seq`가 마스터 테이블에 없는 경우(새로운 품목인 경우), 데이터 무결성을 위해 저장이 생략되거나 마스터 동기화가 먼저 필요함을 로그로 남깁니다.

## 5. 실행 방식
```bash
cd scripts && uv run sync_performance.py
```
또는 `main.py`에 통합할 수 있습니다.
