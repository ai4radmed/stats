# 외부 서비스 설정 및 장애 복구

## 개요

NM-Statistics가 연동하는 외부 서비스의 설정 방법과 장애 시 복구 절차를 정의합니다.

---

## 1. Supabase (도쿄 리전)

- **용도**: Auth, Database (PostgreSQL), RLS, Storage
- **대시보드**: https://supabase.com/dashboard
- **환경변수**: `PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

### 장애 복구
- DB 스키마 복구: `sql_query/rebuild_all_tables.sql` 실행 (멱등성 보장)
- RLS 정책은 SQL 스크립트에 포함

---

## 2. Vercel (서울 리전)

- **용도**: SSR 호스팅, Edge Functions
- **환경변수 관리**: Vercel Dashboard > Settings > Environment Variables

### 장애 복구
- 재배포: `git push` 또는 Vercel Dashboard에서 Redeploy
- 환경변수 누락 시 빌드 실패 → 대시보드에서 확인

---

## 3. Cloudflare (DNS Only)

- **용도**: DNS 관리, Full Strict SSL
- **설정**: Proxy 비활성화 (DNS Only), SSL/TLS → Full (Strict)
