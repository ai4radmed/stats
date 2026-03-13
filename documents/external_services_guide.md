# 외부 서비스 설정 및 검증 절차서

> 이 문서는 nmstats가 의존하는 외부 서비스의 **올바른 설정값**과 **검증 방법**을 정리합니다. 모든 설정은 AI-SDLC 정책을 준수하며, 프로젝트 간 일관성을 유지합니다.

---

## Part 0. 전략적 결정 사항 (Strategic Decisions)

이 프로젝트는 브랜드 일관성과 관리 효율성을 위해 다음과 같은 네이밍 및 도메인 전략을 채택합니다.

- **대표 도메인**: `stats.ai4radmed.com` (Cloudflare에서 관리 중인 `ai4radmed.com`의 서브도메인 활용)
- **GitHub 저장소**: `ai4radmed/stats` (조직 계정 하위에 서비스명 단독 표기)
- **Supabase 프로젝트**: `stats` (조직 `AI4RADMED` 하위에서 서비스명 단독 표기)
- **로컬 프로젝트**: `ai4radmed-stats` (작업 디렉터리 명칭)

---

## Part 1. 서비스별 설정 가이드

### 1. Supabase (Backend/BaaS)
> 데이터베이스, 인증, 스토리지 및 서버리스 로직을 담당하는 핵심 인프라입니다.

#### 1-1. 기본 설정
- **Organization**: `AI4RADMED`
- **Project**: `stats` (또는 `nmstats`)
- **Region**: `Seoul (ap-northeast-2)`
  - *참고: 국내 사용자 대상 서비스를 위해 서울 리전으로 설정하여 지연 시간을 최적화합니다.*

#### 1-2. API 연결 설정 (URL & Keys)
- **Project URL**: `Supabase Dashboard > Settings > API`
- **Anon Key**: 브라우저 클라이언트용 공개 키 (RLS와 함께 동작)
- **Service Role Key**: 서버 사이드 스크립트(데이터 동기화 등) 전용 관리자 키 (절대 노출 금지)

#### 1-3. Authentication (URL Configuration)
인증 성공 후 사용자를 안전하게 복귀시키기 위한 화이트리스트 설정입니다.
**설정 경로**: `Authentication > URL Configuration`

| 항목 | 올바른 값 | 비고 |
| :--- | :--- | :--- |
| **Site URL** | `https://stats.ai4radmed.com` | 최종 운영 도메인 |
| **Redirect URLs** | `http://localhost:4321/auth/callback` | 로컬 개발용 |
| | `https://stats.ai4radmed.com/auth/callback` | 서비스 도메인 콜백 |
| | `https://*-ai4radmed.vercel.app/auth/callback` | Vercel 프리뷰용 |

> [!WARNING]
> 보안을 위해 Redirect URL은 반드시 `/auth/callback` 경로를 포함해야 하며, 와일드카드를 과도하게 사용하지 않습니다.

---

### 2. Vercel (Frontend/Hosting)
> Astro 프레임워크 기반의 웹 서비스를 배포하고 호스팅하는 플랫폼입니다.

#### 2-1. 빌드 및 배포 설정
- **Project**: `stats`
- **Region**: `Seoul (icn1)`
  - *설정 경로: Settings > Functions > Service Region*
- **Framework Preset**: `Astro`
- **Install Command**: `npm install --legacy-peer-deps` (의존성 충돌 방지)

#### 2-2. 환경 변수 (Environment Variables)
프로젝트 실행에 필수적인 키들을 Vercel 대시보드에 등록합니다.

| 변수명 | 용도 | 비고 |
| :--- | :--- | :--- |
| `PUBLIC_SUPABASE_URL` | Supabase API URL | 필수 |
| `PUBLIC_SUPABASE_ANON_KEY` | 클라이언트용 공개 키 | 필수 |
| `SUPABASE_SERVICE_ROLE_KEY` | 서버용 비밀 키 | 데이터 동기화 시 필수 |
| `PUBLIC_LOG_LEVEL` | 로깅 레벨 제어 | `info`, `debug` 등 |

---

### 3. Cloudflare (DNS)
> DNS 관리 및 보안을 담당하며, SSL 처리는 Vercel에 위임합니다.

- **DNS 설정**: Vercel 연동 시 `Proxy (주황 구름)`를 반드시 **비활성화(DNS Only)** 처리합니다.
- **SSL/TLS**: `Full (Strict)` 모드 권장.

---

## Part 2. 기능 검증 체크리스트

설정 변경 후에는 반드시 아래 시나리오를 통해 정상 작동 여부를 확인합니다.

### 2-1. 데이터베이스 접근 및 RLS 검증
| # | 절차 | 예상 결과 |
| :--- | :--- | :--- |
| 1 | SQL Editor에서 `rebuild_all_tables.sql` 실행 | 전체 테이블 및 트리거 정상 생성 |
| 2 | 익명(Anon) 사용자로 `mfds_radpharm_master` 조회 | 읽기 권한(Select) 허용 확인 |
| 3 | 익명 사용자로 데이터 삽입 시도 | 거부 확인 (RLS 보호) |

### 2-2. 데이터 동기화 스크립트 검증 (MFDS API)
| # | 절차 | 예상 결과 |
| :--- | :--- | :--- |
| 1 | `npm run sync:mfds` 실행 (로컬 환경) | 식약처 API 호출 성공 및 데이터 수집 시작 |
| 2 | Supabase 테이블 데이터 확인 | `item_seq` 기준으로 데이터 Upsert 및 `updated_at` 갱신 확인 |
| 3 | 카테고리 분류 확인 (Generator 등) | 제품명 기반 자동 분류 로직 정상 작동 확인 |

---

## Part 3. 장애 복구 가이드

| 서비스 | 증상 | 복구 방법 |
| :--- | :--- | :--- |
| **Supabase** | DB 스키마 손상 | `sql_query/rebuild_all_tables.sql` 재실행 |
| **Vercel** | 배포 오류 (Env 누락) | 1. 대시보드 환경변수 확인<br>2. `git commit --allow-empty`로 재빌드 유도 |
| **Common** | 403 Forbidden | 1. API 키 만료 여부 확인<br>2. Redirect URL 화이트리스트 재점검 |

---
> 마지막 업데이트: 2026-03-13
