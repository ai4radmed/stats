# 페이지 명세: src/pages/index.astro

## 역할
- 서비스의 메인 진입점
- 핵의학 검사 통계 요약 및 브랜딩 메시지 표시

## 주요 위젯/컴포넌트
- `Hero`: 서비스 소개 및 주요 기능 하이라이트
- `StatsSummary`: 주요 통계 지표 요약 (목업 데이터 우선)
- `Footer`: 하단 네비게이션 및 정보

## 데이터 Flow
- (추후) Supabase에서 최신 통계 요약 데이터를 서버 사이드에서 Fetch 하여 렌더링

## 핵심 규칙
- `prerender = false` 강제 (SSR)
- PWA 지원을 위한 메타 태그 포함
