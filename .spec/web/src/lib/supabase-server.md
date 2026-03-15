# 모듈 명세: src/lib/supabase-server.ts

## 역할
- 서버 사이드(Astro Actions, Pages)에서 Supabase에 접근하는 클라이언트 제공
- SSR 세션 및 RLS 대응

## 기능 (API)
- `createSupabaseServerClient(request, cookies)`: 서버 사이드 인증 세션을 처리하는 클라이언트 생성
- `supabaseAnon`: 서버 사이드 전용 익명 클라이언트 (쿠키 불필요)
- `supabaseAdmin`: 서비스 롤 키를 사용하며 RLS를 우회하는 관리자 클라이언트

## 핵심 규칙
- `supabaseAdmin`은 서버 사이드 비즈니스 로직에서만 사용하며 절대 클라이언트에 직접 노출 금지
- 환경변수 `PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` 필수
