# sync_performance.py 테스트 명세

## 1. 개요
`sync_performance.py`의 핵심 로직(API 호출, 데이터 파싱, DB 저장 준비)이 의도대로 작동하는지 검증합니다.

## 2. 테스트 환경
- **프레임워크**: Pytest
- **Mocking**: `httpx`를 이용한 외부 API 호출 모킹, `supabase` 클라이언트 모킹

## 3. 테스트 케이스

### T1: API 응답 파싱 테스트 (Mock)
- **목적**: 캡처 화면에서 확인된 `items -> item` 구조를 올바르게 파싱하는지 확인.
- **입력**: 캡처 내용과 동일한 구조의 가짜 JSON 응답.
- **기대 결과**: 리스트 내에 `item_seq`, `DATE_YEAR`, `AMT` 등이 추출된 객체가 생성됨.

### T2: 데이터 필터링 및 매핑 테스트
- **목적**: 수집된 데이터가 DB 테이블 구조(`item_seq`, `year`, `result_part`, `amount`)에 맞게 변환되는지 확인.
- **기대 결과**: `AMT` 값이 정수(int)로 정상 변환되고, `ITEM_SEQ`가 `item_seq` 필드에 할당됨.

### T3: DB Upsert 호출 테스트 (Mock)
- **목적**: `supabase.table().upsert().execute()`가 올바른 인자(item_seq, year, result_part 포함)로 호출되는지 확인.

## 4. 실행 방식
```bash
cd scripts && uv run pytest test_sync_performance.py
```
