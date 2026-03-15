# 페이지 명세: src/pages/master-list.astro

## 역할
- 식약처(MFDS)에서 수집된 방사성의약품 마스터 목록 표시
- 카테고리(제너레이터, 키트, 완제품) 및 ATC 코드별 필터링 제공

## 주요 위젯/컴포넌트
- `ApiStatusCard`: 데이터 수집 상태 정보 표시 (최종 동기화 시간, 총 API 호출 횟수, 수집된 총 품목 수, 호출 제한 대비 사용량(10,000))
- `MasterTable`: 의약품 목록을 그리드/테이블 형태로 표시 (No., 품목코드, 제품명, 업체명, 카테고리, ATC코드, 주요성분, 허가일자, 취소일자, 생성일시, 수정일시, EDI코드 - 총 12개 필드)
- `CategoryFilter`: 카테고리별 필터링 탭 또는 드롭다운
- `SearchBar`: 제품명/업체명 검색 기능

## 데이터 Flow
- **Source**: Supabase `mfds_radpharm_master` 테이블
- **Fetch**: Astro Server-side에서 데이터 수집 (`supabase-server.ts` 사용)
- **Logic**: 
  - 검색어 및 필터 조건에 따른 서버 사이드 쿼리 처리
  - 데이터가 없을 경우 "데이터가 없습니다" 메시지 표시

## 핵심 규칙
- `prerender = false` (SSR)
- 데이터 로딩 속도 최적화를 위해 필요한 필드만 Select
- 200줄 원칙 준수 (복잡한 UI 로직은 컴포넌트로 분리)
