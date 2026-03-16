# stats-ai4radmed 아키텍처 (Triple-Stack)

이 문서는 AI 에이전트의 **통합 진입점(System Map)**입니다.
모든 작업은 이 문서 → `.spec/` 명세 → 구현 순서로 수행합니다.

---

## 1. 기술 스택 (Triple-Stack)

| 레이어 | 기술 | 핵심 도구 |
| :--- | :--- | :--- |
| **Frontend (UI)** | Astro 5.x (SSR), PWA | npm, .node-version |
| **Backend (Orchestration)** | Python 3.12+ | uv (pyproject.toml) |
| **Analytics (Engine)** | R (Statistics) | renv (renv.lock) |
| **Infrastructure** | Vercel (Web), Supabase (Auth/DB) | - |
| **Quality** | ESLint, Vitest, Pytest, Makefile | - |

---

## 2. 코드 구조 및 명세 매핑

각 소스 파일은 `.spec/` 디렉터리에 1:1 대응하는 명세를 가집니다.

| 소스 경로 | 명세 경로 | 역할 |
| :--- | :--- | :--- |
| `web/src/` | `.spec/web/src/*.md` | Astro UI 및 사용자 시각화 로직 |
| `scripts/` | `.spec/scripts/*.md` | Python 오케스트레이션 및 데이터 파이프라인 |
| `analysis/` | `.spec/analysis/*.md` | R 통계 분석 엔진 및 라이브러리 |
| `sql_query/` | `.spec/sql_query/*.md` | Supabase DB 스키마 및 RLS 정책 |

### 핵심 격리 경로 (Ignore List)
- **Web**: `web/node_modules/`, `web/dist/`, `web/.astro/`, `web/test-results/`
- **Scripts**: `scripts/.venv/`, `scripts/__pycache__/`
- **Analysis**: `analysis/renv/library/`, `analysis/.RData`

---

## 3. 명세 계층 (Specification Hierarchy)

1. **Level 1 — System Map**: 본 문서. 전체 구조와 정책.
2. **Level 2 — File Spec**: `.spec/` 내 개별 명세. 역할, API, 핵심 규칙.
3. **Level 3 — Implementation**: `web/`, `scripts/`, `analysis/` 등 소스 코드.

---

## 4. 개발 워크플로우 (Multi-Stack Spec-First)

1. **Plan** — 작업 지시 수령 → 레이어별 타겟 파일 및 명세 도출.
2. **Manifest** — `.spec/` 하위(web, scripts, analysis)에 명세 작성/갱신.
3. **Execute** — 명세 기반으로 구현체 작성. 
   - **웹**: `web/` 경로에서 개발 및 테스트.
   - **데이터**: `scripts/` 및 `analysis/` 경로에서 분석 로직 개발.
4. **Verify** — `Makefile`을 통한 통합 검증 실행.

### 통합 관리 (Makefile)
- `make sync`: git pull 실행 후 uv, renv, npm 환경을 최신화(Sync).
- `make run-stats`: Python이 R을 실행하여 최신 통계 데이터 생성.
- `make dev`: Astro 개발 서버 실행.

---

## 5. 핵심 정책

- **데이터 파이프라인**: Python이 R 스크립트를 관리하고, 결과는 `web/public/data/`에 JSON으로 저장한다.
- **환경 독립성**: 각 레이어는 전용 도구(uv, renv, node-version)로 완벽히 격리한다.
- **환경 변수 동기화**: 프로젝트 루트의 `.env`를 원본으로 하며, `web/` 디렉터리에는 심볼릭 링크(`ln -s ../.env web/.env`)를 생성하여 통합 관리한다.
- **200줄 원칙 (Complexity Control)**: 하나의 구현체 파일은 200줄 이하로 유지하며, 초과 시 모듈화한다.
- **SDLC 사이클 (Atomic Cycle)**: `명세(Spec) -> 구현(Implementation) -> 테스트 명세(Test Spec) -> 테스트 구현(Test Code)`의 사이클을 하나라도 생략하지 않고 완수한다.
- **Fail Loudly**: 특히 데이터 분석 단계의 에러는 Python 로그를 통해 명확히 남긴다.

---

## 6. 상세 참조 문서

| 문서 | 용도 |
| :--- | :--- |
| [DEVELOPERS.md](documents/DEVELOPERS.md) | 개발자를 위한 상세 시스템 개요 및 레이어별 가이드 |
| [database_schema.md](documents/database_schema.md) | Supabase ERD 및 RLS 정의 |
| [external_services_guide.md](documents/external_services_guide.md) | Supabase/Vercel 설정 가이드 |
| [test_strategy.md](documents/test_strategy.md) | 계층별(Web/Script/R) 테스트 전략 |
