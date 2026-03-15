# nmstats 데이터베이스 스키마

이 문서는 nmstats 프로젝트의 Supabase PostgreSQL 데이터베이스 구조를 설명합니다.

> **Note:** 모든 테이블 스키마 정의와 마이그레이션은 `sql_query/rebuild_all_tables.sql` 파일 하나로 통합 관리됩니다. (멱등성 보장)

## 스키마 개요

- **데이터베이스 엔진**: PostgreSQL
- **기본 스키마**: `public`

## 주요 테이블

### 1. `profiles`
사용자 기본 정보 및 권한 상태를 관리합니다. (Auth 연동)

| 필드명 | 타입 | 설명 | 기본값 |
| :--- | :--- | :--- | :--- |
| `id` | `uuid` (PK) | `auth.users.id` 참조 | |
| `email` | `text` | 사용자 이메일 | |
| `is_admin` | `boolean` | 관리자 여부 | `false` |
| `created_at` | `timestamptz` | 생성 일시 | `now()` |

### 2. `mfds_radpharm_master` (식약처 마스터)
식약처 API(Service07)를 통해 수 수집된 방사성의약품 마스터 데이터입니다.

| 필드명 | 타입 | 설명 | 비고 |
| :--- | :--- | :--- | :--- |
| `item_seq` | `text` (PK) | 품목기준코드 | 고유식별자 |
| `item_name` | `text` | 제품명 (한글) | Not Null |
| `entp_name` | `text` | 업체명 | Not Null |
| `atc_code` | `text` | ATC 분류 코드 | V09, V10 등 |
| `category` | `text` | 제품 분류 | Generator, Kit, Finished |
| `edi_code` | `text` | HIRA EDI 코드 | 매핑용 |
| `main_item_ingr`| `text` | 주요 성분 | |
| `item_permit_date`| `date` | 허가일자 | |
| `cancel_date` | `date` | 취소/만료일자 | |
| `item_class_no` | `text` | 분류번호 | 예: 431 |
| `created_at` | `timestamptz` | 생성 시각 | `now()` |
| `updated_at` | `timestamptz` | 최종 수정 시각 | 트리거 자동 갱신 |

### 3. `nm_test_stats` (심평원 통계 - 예정)
심평원(HIRA)으로부터 수집될 실제 검사 행위 통계 데이터입니다.

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `id` | `bigint` (PK) | 자동 증가 ID |
| `edi_code` | `text` | EDI 코드 (FXXXX) |
| `test_name` | `text` | 검사/행위 명칭 |
| `count` | `integer` | 실시 건수 |
| `year_month` | `text` | 통계 구분 (YYYYMM) |
| `hosp_type` | `text` | 요양기관 종별 |

### 4. `api_sync_log` (API 수집 로그)
데이터 수집 파이프라인의 실행 결과 및 통계를 관리합니다.

| 필드명 | 타입 | 설명 | 기본값 |
| :--- | :--- | :--- | :--- |
| `id` | `bigint` (PK) | 자동 증가 ID | |
| `sync_source` | `text` | 수집 출처 (예: MFDS) | |
| `request_count` | `integer` | API 호출 성공 횟수 | `0` |
| `item_count` | `integer` | 수집된 데이터(품목) 수 | `0` |
| `status` | `text` | 실행 상태 (SUCCESS, FAIL) | |
| `created_at` | `timestamptz` | 생성 시각 | `now()` |

---

## 인덱스 및 성능
- `idx_mfds_radpharm_atc`: ATC 코드 기반 필터링 최적화
- `idx_mfds_radpharm_edi`: EDI 코드 기반 매핑 최적화

---

## SQL 스크립트 관리
`sql_query/rebuild_all_tables.sql`을 실행하면 전체 스키마(RLS 정책 포함)가 복구/업데이트됩니다.
