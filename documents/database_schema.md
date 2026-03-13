# nmstats 데이터베이스 스키마

이 문서는 nmstats 프로젝트의 Supabase PostgreSQL 데이터베이스 구조를 설명합니다.

> **Note:** 모든 테이블 스키마 정의와 마이그레이션은 `sql_query/rebuild_all_tables.sql` 파일 하나로 통합 관리됩니다. (멱등성 보장)

## 스키마 개요

- **데이터베이스 엔진**: PostgreSQL
- **기본 스키마**: `public`

## 주요 테이블 (예정)

### 1. `profiles`
사용자 기본 정보 및 권한 상태를 관리합니다.

| 필드명 | 타입 | 설명 | 기본값 |
| :--- | :--- | :--- | :--- |
| `id` | `uuid` (PK) | `auth.users.id` 참조 | |
| `email` | `text` | 사용자 이메일 | |
| `is_admin` | `boolean` | 관리자 여부 | `false` |
| `created_at` | `timestamp` | 생성 일시 | `now()` |

### 2. `nm_test_stats` (예시)
핵의학 검사 통계 데이터를 저장합니다.

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `id` | `bigint` (PK) | 고유 식별자 |
| `test_name` | `text` | 검사명 |
| `test_count` | `integer` | 검사 건수 |
| `year_month` | `text` | 통계 년월 (YYYY-MM) |
| `created_at` | `timestamp` | 등록 일시 |

---

## RPC 함수 및 RLS 정책
관리자 권한 확인을 위한 전용 함수(`is_current_user_admin()`)를 사용하여 RLS 무한 재귀를 방지합니다.

---

## SQL 스크립트 관리
`sql_query/rebuild_all_tables.sql`을 실행하면 전체 스키마가 복구/업데이트됩니다.
