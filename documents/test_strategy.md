# 테스트 전략

## 개요

nmstats의 자동화 테스트 시나리오 및 수동 점검 항목을 정의합니다.

---

## 1. 단위 테스트 (Vitest)

- **경로**: `tests/unit/**/*.test.ts`
- **실행**: `npm run test:unit`
- **원칙**: 구현체와 1:1 매칭 (`.spec/tests/unit/` 명세 기반)

### 대상
| 모듈 | 검증 항목 |
|------|----------|
| `src/lib/logger.ts` | 로그 레벨 필터링, JSON 포맷 출력 |
| `src/lib/supabase-server.ts` | 클라이언트 생성, admin fallback |
| `src/lib/supabase-browser.ts` | 쿠키 백업/복원 로직 |

---

## 2. E2E 테스트 (Playwright)

- **경로**: `tests/e2e/**/*.spec.ts`
- **실행**: `npm run test:e2e`
- **브라우저**: Chromium

### 시나리오 (예정)
- 퍼블릭 페이지 접근 및 렌더링 확인
- 오프라인 모드에서 캐시된 페이지 표시

---

## 3. 배포 전 자동 검증 (Husky pre-commit)

```
astro check → npm run test:unit → lint-staged
```

---

## 4. 수동 점검 항목

- [ ] Vercel 배포 후 프로덕션 URL 접근 확인
- [ ] PWA 설치 및 오프라인 동작 확인
- [ ] Supabase 대시보드에서 DB 연결 상태 확인
