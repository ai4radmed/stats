# nmstats (ai4radmed-stats) 개발자 가이드

이 프로젝트는 **핵의학 진료통계 조회**를 위한 시스템을 **Astro(UI), Python(Orchestration), R(Analytics)** 기반으로 구축한 다층 아키텍처(Triple-Stack) 시스템입니다.

---

## 1. 아키텍처 개요 (Triple-Stack)

본 프로젝트는 각 언어의 강점을 극대화하기 위해 세 개의 독립적인 레이어로 구성됩니다.

### A. Frontend (web/)
- **기술**: Astro 5.x (SSR), PWA
- **역할**: 사용자 인터페이스 제공, 분석 데이터 시각화
- **환경 관리**: `npm`, `.node-version`

### B. Backend / Orchestration (scripts/)
- **기술**: Python 3.12+ (uv)
- **역할**: 데이터 수집 파이프라인 제어, R 스크립트 실행 자동화, DB 연동
- **환경 관리**: `uv`, `pyproject.toml`

### C. Analytical Engine (analysis/)
- **기술**: R (renv)
- **역할**: 의료 통계 분석, ggplot2 기반 고품질 시각화 데이터 생성
- **환경 관리**: `renv`, `renv.lock`

---

## 2. 개발 워크플로우 (Spec-First)

모든 개발은 `.spec/` 디렉터리의 명세를 중심으로 진행됩니다.

1.  **Plan**: 작업 지봉 수령 후 타겟 레이어(Web/Scripts/Analysis) 결정.
2.  **Manifest**: `.spec/` 하위 해당 경로에 명세(API, 규칙) 작성.
3.  **Execute**: 명세 기반 구현체 작성.
4.  **Verify**: `Makefile`을 통한 통합 검증.

---

## 3. 핵심 디렉터리 구조

| 경로 | 설명 |
| :--- | :--- |
| `web/` | **Frontend**: Astro 웹 서비스 (node_modules, .astro 격리) |
| `scripts/` | **Backend**: Python 오케스트레이터 (.venv 격리) |
| `analysis/` | **Analytics**: R 통계 분석 엔진 (renv/library 격리) |
| `.spec/` | 각 레이어별 1:1 대응 명세서 |
| `sql_query/` | Supabase DB 스키마 및 RLS 정책 관리 |
| `web/public/data/` | R이 분석한 결과(JSON/SVG)가 저장되는 공유 데이터 공간 |

---

### 최신 환경 동기화 (Sync)
```bash
make sync
```

### 데이터 분석 실행 (Update Stats)
```bash
make run-stats
```

### 웹 개발 서버 실행
```bash
make dev
```

---

## 4. 환경 변수 설정 (.env)

본 프로젝트는 보안 및 데이터 수집을 위한 환경 변수를 프로젝트 루트의 `.env` 파일에서 통합 관리합니다.

### 중앙 집중식 관리
1.  **원본 파일**: 프로젝트 루트 디렉터리에 `.env` 파일을 생성하고 필요한 Key(Supabase, MFDS_KEY 등)를 입력합니다.
2.  **웹 레이어 연결**: Astro(Frontend)는 프로젝트 루트의 `.env`를 자동으로 인식하지 못하므로, `web/` 디렉터리에 **심볼릭 링크**를 생성하여 동기화합니다.

```bash
# 루트 디렉터리에서 실행
ln -s ../.env web/.env
```

이렇게 설정하면 루트의 `.env` 파일 하나만 수정해도 Python(Scripts)과 Astro(Web) 레이어에 즉시 반영됩니다.

---

## 5. 설계 철학

- **격리(Isolation)**: 각 레이어는 자신만의 환경 관리 도구(uv, renv, node)를 가지며 서로의 의존성을 침범하지 않습니다.
- **데이터 흐름**: `DB -> Python/R -> JSON -> Astro` 순으로 한 방향으로만 흐릅니다.
- **Fail Loudly**: 특히 R 통계 분석 레이어의 에러는 Python 로그를 통해 즉각적으로 인지되도록 설계되었습니다.

---
> 마지막 업데이트: 2026-03-15 (Triple-Stack Re-architecture)
