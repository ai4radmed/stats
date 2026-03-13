# Table Spec: `mfds_radpharm_master`

방사성의약품 마스터 정보를 저장하는 테이블 명세입니다.

## 1. 개요
- **목적**: 식약처 OpenAPI로부터 수집된 방사성의약품 데이터를 관리하고, 심평원 통계 매핑의 기준점으로 활용.
- **매핑 소스**: 식약처 의약품 제품 허가정보 OpenAPI (`atc_code` V09, V10 기반)

## 2. 컬럼 상세

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `item_seq` | `TEXT` | `PRIMARY KEY` | 품목기준코드 (식약처 고유 ID) |
| `item_name` | `TEXT` | `NOT NULL` | 제품명 (한글) |
| `entp_name` | `TEXT` | `NOT NULL` | 업체명 |
| `atc_code` | `TEXT` | | ATC 분류 코드 (V09, V10 등) |
| `category` | `TEXT` | | 항목 유형 (Generator, Kit, Finished) |
| `edi_code` | `TEXT` | | 건강보험심사평가원 EDI 코드 |
| `main_item_ingr` | `TEXT` | | 제품의 주요 유효 성분 |
| `item_permit_date`| `DATE` | | 최초 품목 허가 일자 |
| `cancel_date` | `DATE` | | 허가 취소 또는 만료 일자 |
| `item_class_no` | `TEXT` | | 식약처 분류번호 (예: 431) |
| `created_at` | `TIMESTAMPTZ`| `DEFAULT now()` | 데이터 생성 시각 |
| `updated_at` | `TIMESTAMPTZ`| `DEFAULT now()` | 데이터 최종 수정 시각 |

## 3. 유동성 로직 (Business Rules for Agent)
- **Insert/Update**: `item_seq`를 기준으로 **Upsert**를 수행한다.
- **Category Assignment**: `item_name`에 "제너레이터" 포함 시 `Generator`, "키트" 포함 시 `Kit`, 둘 다 아닐 시 `Finished`로 값을 설정한다.
- **Index**: 자주 조회되는 `atc_code`와 `edi_code`에 대해 인덱스 생성을 고려한다.

## 4. 관계 (Relations)
- 향후 `nm_test_stats` 테이블과 `edi_code`를 매개로 Join 하여 통계를 산출한다.
