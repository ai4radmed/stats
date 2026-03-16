# Specification: Clinical Trial Data Sync (MFDS)

식약처 의약품 임상시험 정보조회 서비스를 통해 특정 제품명(예: 177Lu)을 포함하는 임상시험 정보를 수집하고 DB에 저장합니다.

## 1. 역할 (Role)
- 식약처 OpenAPI(`MdcincLincTestInfoService02`)를 호출하여 임상시험 정보를 검색합니다.
- 수집된 정보를 `mfds_clinical_trials` 테이블에 최신 상태로 유지(Upsert)합니다.
- 성공 및 실패 여부를 로그로 남깁니다.

## 2. 데이터 흐름 (Data Flow)
1. **Source**: 식약처 OpenAPI - `getMdcincLincTestInfoList02`
2. **Transform**: XML 응답을 파싱하여 DB 스키마에 맞는 JSON 구조로 변환.
3. **Destination**: Supabase Table `mfds_clinical_trials`

## 3. 핵심 기능 (Core Features)

### A. API 호출 (Fetch)
- **Base URL**: `https://apis.data.go.kr/1471000/MdcincLincTestInfoService02/getMdcincLincTestInfoList02`
- **Method**: GET
- **Parameters**:
  - `serviceKey`: 인증키 (환경변수 `MFDS_SERVICE_KEY`)
  - `goods_name`: 검색 제품명 (예: '177Lu')
  - `pageNo`: 페이지 번호 (기본 1)
  - `numOfRows`: 페이지당 결과 수 (기본 100)
  - `type`: json (지원하지 않을 경우 XML 파싱 필요)

### B. 데이터 매핑 (Mapping)
| API 필드 | DB 필드 | 설명 |
| :--- | :--- | :--- |
| `CLINIC_TEST_SN` | `clinic_test_sn` | (PK) 임상시험 일련번호 |
| `GOODS_NAME` | `goods_name` | 제품명 |
| `APPLY_ENTP_NAME` | `entp_name` | 신청인/업체명 |
| `APPROVAL_TIME` | `approval_time` | 승인일자 (YYYYMMDD -> DATE) |
| `CLINIC_EXAM_TITLE` | `clinic_exam_title` | 임상시험 제목 |
| `CLINIC_STEP_NAME` | `clinic_step_name` | 임상시험 단계 |
| `LAB_NAME` | `lab_name` | 실시기관 |

### C. 동기화 로직 (Sync Logic)
- `clinic_test_sn`을 기준으로 `upsert`를 수행합니다.
- `approval_time`이 `YYYYMMDD` 형식인 경우 `YYYY-MM-DD`로 변환하여 저장합니다.

## 4. 예외 처리 (Exception Handling)
- **Fail Loudly**: API 호출 실패, 파싱 에러, DB 연결 에러 시 상세 로그를 남기고 종료합니다.
- **Empty Result**: 검색 결과가 없을 경우 경고 로그를 남기고 정상 종료합니다.

## 5. 테스트 명세 (Test Spec)
- **Unit Test**: API 응답(XML/JSON) 모킹을 통한 파싱 로직 검증.
- **Integration Test**: 실제 API 호출 및 Supabase 데이터 적재 확인 (CLI 환경).
