# File Spec: scripts/test_main.py (Test)

본 문서는 `scripts/main.py`의 기능적 정합성을 검증하기 위한 테스트 명세입니다.

## 1. 테스트 목적
식약처 API 호출부터 Supabase 적재까지의 데이터 파이프라인이 설계 명세(`documents/data_collection_methodology.md`)대로 작동하는지 자동화된 테스트를 통해 확인합니다.

## 2. 테스트 항목 및 검증 포인트

### ① API 호출 및 파이프라인 (Mock Test)
- **대상**: `fetch_mfds_data`
- **검증**: 
    - API 키가 포함된 Full URL이 올바르게 생성되는가?
    - 401, 500 에러 시 적절한 에러 로그를 남기고 중단되는가?
    - JSON 응답 데이터가 리스트 형태로 정상 반환되는가?

### ② 카테고리 분류 로직 (Unit Test)
- **대상**: `classify_category`
- **검증**:
    - 제품명에 '제너레이터' 포함 시 -> `Generator` 반환
    - 제품명에 '키트' 또는 'kit' 포함 시 -> `Cold Kit` 반환
    - 그 외의 경우 -> `Finished` 반환

### ③ 데이터 정합성 (Schema Test)
- **대상**: `sync_to_supabase` (Mocked Supabase)
- **검증**:
    - API 응답의 CamelCase 또는 대문자 필드가 DB의 snake_case 필드로 정확히 매핑되는가?
    - `item_seq`가 문자열(String)로 형변환되어 저장되는가?

## 3. 테스트 환경
- **도구**: `pytest`
- **실행**: `pytest scripts/test_main.py`
