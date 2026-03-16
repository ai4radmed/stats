# mfds_item_performance 테이블 명세

## 1. 개요
방사성의약품의 연도별 생산 및 수입 실적 데이터를 저장하는 테이블입니다. `mfds_radpharm_master` 테이블의 품목들과 1:N 관계를 가집니다.

## 2. 테이블 스키마 (PostgreSQL)

| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| **id** | BIGINT | PRIMARY KEY, GENERATED ALWAYS | 레코드 고유 ID |
| **item_seq** | TEXT | REFERENCES mfds_radpharm_master(item_seq) | 품목기준코드 (외래키) |
| **year** | TEXT | NOT NULL | 실적 연도 (DATE_YEAR, 예: "2024") |
| **result_part** | TEXT | NOT NULL | 실적 구분 ("수입", "생산" 등 / RESULT_PART) |
| **amount** | BIGINT | DEFAULT 0 | 실적 금액 (AMT) |
| **entp_name** | TEXT | - | 업체명 (데이터 검증용 / ENTP_NAME) |
| **item_name** | TEXT | - | 제품명 (데이터 검증용 / ITEM_NAME) |
| **created_at** | TIMESTAMPTZ | DEFAULT now() | 데이터 생성 시각 |
| **updated_at** | TIMESTAMPTZ | DEFAULT now() | 데이터 최종 수정 시각 |

## 3. 핵심 비즈니스 규칙
- **중복 방지**: 한 품목(`item_seq`)에 대해 동일한 연도(`year`)와 동일한 실적 구분(`result_part`)을 가진 데이터는 하나만 존재해야 합니다. (`UNIQUE (item_seq, year, result_part)`)
- **데이터 무결성**: `item_seq`가 없는 실적 데이터는 저장하지 않거나, 마스터 테이블에 먼저 등록된 경우에만 연결합니다.
- **업데이트 전략**: 동일 키값이 존재할 경우 `amount` 정보를 최신화(Upsert)합니다.

## 4. 인덱스 설정
- `idx_performance_item_seq`: `item_seq` 필드에 인덱스를 생성하여 조인 성능 향상
- `idx_performance_year`: 특정 연도별 통계 조회를 위한 인덱스

## 5. RLS 정책
- **SELECT**: 모든 사용자(Authenticated/Anon)가 읽을 수 있습니다.
- **INSERT/UPDATE/DELETE**: 관리자 권한을 가진 사용자(Python Backend 서비스 롤 등)만 가능합니다.
