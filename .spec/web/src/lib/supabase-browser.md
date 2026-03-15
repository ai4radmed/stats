# 모듈 명세: src/lib/supabase-browser.ts

## 역할
- 브라우저 사이드(Client Components)에서 Supabase에 접근하는 클라이언트 제공
- PWA 환경에서의 세션 유지 보강

## 기능 (API)
- `supabase`: 싱글톤 브라우저 클라이언트

## 핵심 규칙
- iOS PWA 등 쿠키 소실 대응을 위한 localStorage 백업/복원 로직 포함
- PKCE 플로우 유지
