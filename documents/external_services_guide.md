# 외부 서비스 설정 및 검증 절차서

> 이 문서는 **ai4radmed-stats (통계 시스템)**가 의존하는 외부 서비스의 **올바른 설정값**과 **검증 방법**을 정리합니다. 모든 설정은 AI-SDLC 정책을 준수하며, 프로젝트 간 일관성을 유지합니다.

---

## Part 0. 전략적 결정 사항 (Strategic Decisions)

이 프로젝트는 브랜드 일관성과 관리 효율성을 위해 다음과 같은 네이밍 및 도메인 전략을 채택합니다.

- **대표 도메인**: `stats.ai4radmed.com` (Cloudflare에서 관리 중인 `ai4radmed.com`의 서브도메인이자 Vercel 연동)
- **GitHub 저장소**: `ai4radmed/stats`
- **Supabase 공식 프로젝트**: `stats` (조직 `AI4RADMED` 하위)
- **로컬 프로젝트**: `ai4radmed-stats`

---

## Part 1. 서비스별 설정 가이드

### 1. Supabase (Backend/BaaS)

> 데이터베이스, 인증, 실시간 통계 시각화를 위한 핵심 인프라입니다.

#### 1-1. 기본 설정 (Project)
- **Organization**: `AI4RADMED`
- **Project Name**: `stats`
- **Region**: `Seoul (ap-northeast-2)`
  - *참고: 지연 시간 최적화를 위해 반드시 서울 리전으로 설정합니다.*

#### 1-2. API 연결 설정 (URL & Keys)
> 앱이 Supabase와 대화하기 위한 **통로(URL)**와 **열쇠(Keys)**를 확보하는 단계입니다.

- **Project URL (API URL)**:
    - **확인 경로**: `Supabase Dashboard > Integrations > Data API`
    - **특징**: RESTful API 엔드포인트로 클라이언트(Astro) 및 서버(Python) 통신에 사용됩니다.
- **API Keys (열쇠)**:
    - **확인 경로**: `Supabase Dashboard > Settings > API Keys`
    - **Publishable key (Anon Key)**: 브라우저(Front-end)에서 안전하게 사용됩니다. RLS 보안 기능과 함께 동작합니다.
    - **Secret key (Service Role Key)**: **마스터키**입니다. RLS를 무시하므로 Python 데이터 수집 스크립트(`scripts/`)에서만 사용하며 절대 외부에 노출하지 않습니다.

#### 1-3. Authentication (인증 및 리다이렉트)
> 사용자가 안전하게 로그인하고 복귀할 수 있도록 설정합니다.

**설정 경로**: `Supabase Dashboard > Authentication > URL Configuration`

| 항목 | 올바른 값 | 비고 |
| :--- | :--- | :--- |
| **Site URL** | `https://stats.ai4radmed.com` | 최종 운영 도메인 |
| **Redirect URLs** | `http://localhost:4321/auth/callback` | 로컬 개발용 |
| | `https://stats.ai4radmed.com/auth/callback` | 서비스 도메인 콜백 |
| | `https://*-ai4radmed.vercel.app/auth/callback` | Vercel 프리뷰용 |

> [!WARNING]
> 보안을 위해 Redirect URL은 반드시 `/auth/callback` 경로를 포함해야 하며, 와일드카드를 과도하게 사용하지 않습니다.

#### 1-4. Database & SQL
- **Master Table**: `mfds_radpharm_master` (방사성의약품 마스터)
- **초기화 스크립트**: `sql_query/rebuild_all_tables.sql`
- **RLS 정책**:
  - `Allow public read access`: 누구나 통계 조회 가능
  - `Admin write access`: Service Role Key를 가진 관리자(Python 스크립트)만 수정 가능

---

### 2. Vercel (Frontend/Hosting)

> Astro 프레임워크 기반의 웹 서비스를 배포하고 호스팅하는 플랫폼입니다.

#### 2-1. 설정 (Project & Region)
- **Project**: `stats`
- **Region**: `Seoul (icn1)`
  - **설정 경로**: `Settings > Functions > Service Region`
  - **중요**: 한국 내 원활한 데이터 시각화를 위해 반드시 서울로 지정합니다.

#### 2-2. 환경 변수 (Environment Variables)
> 프로젝트 실행에 필수적인 키들을 Vercel 대시보드에 등록합니다.

| 변수명 | 적용 범위 | 설명 |
| :--- | :--- | :--- |
| `PUBLIC_SUPABASE_URL` | All | Supabase API URL |
| `PUBLIC_SUPABASE_ANON_KEY` | All | 클라이언트용 공개 키 |
| `SUPABASE_SERVICE_ROLE_KEY` | All | 서버용 비밀 키 (Data Sync 전용) |
| `PUBLIC_LOG_LEVEL` | All | 로깅 레벨 (`info`, `debug`) |

#### 2-3. 빌드 설정 (Build Settings)
| 항목 | 값 | 비고 |
| :--- | :--- | :--- |
| **Framework Preset** | `Astro` | |
| **Install Command** | `npm install --legacy-peer-deps` | 의존성 충돌 방지용 필수 옵션 |
| **Build Command** | `npm run build` | |

---

### 3. Cloudflare (DNS/Security)

> 도메인 `ai4radmed.com`의 DNS 관리를 담당합니다.

- **DNS Records**:
  - `Type`: `CNAME`
  - `Name`: `stats`
  - `Target`: `cname.vercel-dns.com`
  - **Proxy Status**: `DNS Only` (회색 구름)
    - *이유: Proxy를 켜면 Vercel과 SSL 충돌이 발생할 수 있으므로 반드시 꺼야 합니다.*
- **SSL/TLS Mode**: `Full (Strict)` 권장

---

## Part 2. 기능 검증 체크리스트

> 설정 변경 후에는 반드시 아래 시나리오를 통해 정상 작동 여부를 확인합니다.

### 2-1. 데이터베이스 및 RLS 검증
| # | 절차 | 예상 결과 |
| :--- | :--- | :--- |
| 1 | SQL Editor에서 `rebuild_all_tables.sql` 실행 | 전체 테이블 및 트리거 정상 생성 |
| 2 | 익명(Anon) 사용자로 페이지 접속 (또는 API 호출) | 방사성의약품 마스터 데이터 조회 성공 |
| 3 | 익명 사용자로 데이터 수정/삭제 시도 | `403 Forbidden` 또는 RLS에 의한 거부 |

### 2-2. 데이터 동기화 (Python-R 파이프라인)
| # | 절차 | 예상 결과 |
| :--- | :--- | :--- |
| 1 | `make run-stats` 실행 (로컬 환경) | 식약처 API 호출 → R 분석 → Supabase 적재 성공 |
| 2 | Supabase 테이블 데이터 확인 | 신규 데이터 Upsert 및 `updated_at` 갱신 확인 |
| 3 | `web/public/data/` 파일 확인 | 분석 결과 JSON 파일이 갱신되어야 함 |

### 2-3. 도메인 및 SSL 연결
| # | 절차 | 예상 결과 |
| :--- | :--- | :--- |
| 1 | `https://stats.ai4radmed.com` 접속 | 사이트 정상 접속 및 자물쇠 아이콘 표시 |
| 2 | `http://stats.ai4radmed.com` (80포트) 접속 | 자동으로 HTTPS로 리다이렉트 (HSTS 활성화) |

---

## Part 3. 장애 복구 및 트러블슈팅

### 3-1. 자주 발생하는 장애 패턴 및 해결

| 서비스 | 증상 | 원인 | 해결 방법 |
| :--- | :--- | :--- | :--- |
| **Supabase** | `403 Forbidden` (Read) | RLS 정책 미설정 | `rebuild_all_tables.sql` 정책 구문 재점검 |
| **Vercel** | 배포 오류 (Env 누락) | Vercel 대시보드 환경변수 미등록 | `Settings > Environment Variables` 확인 후 재빌드 |
| **Scripts** | API 호출 권한 에러 | Service Role Key 유출 또는 만료 | Supabase에서 키 재발급 후 Vercel/로컬 업데이트 |
| **DNS** | 연결 시간 초과 | Cloudflare Proxy 설정 오류 | 주황색 구름 → 회색 구름(DNS Only)으로 변경 |

### 3-2. CDN 캐시 무효화 (Vercel 특이사항)
정적 파일이 갱신되었음에도 브라우저에서 옛날 데이터가 보인다면 아래 명령으로 강제 재빌드를 수행합니다.

```bash
git commit --allow-empty -m "fix: clear cdn cache"
git push
```

---
> 마지막 업데이트: 2026-03-15 (Triple-Stack Re-architecture 반영)
