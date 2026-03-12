# 모듈 명세: src/lib/logger.ts

## 역할
- 프로젝트 전반에 걸친 정형화된(JSON) 로깅 유틸리티
- 환경변수(`PUBLIC_LOG_LEVEL`)에 따른 노출 제어

## 기능 (API)
- `createLogger(module: string)`: 특정 모듈명을 가진 로거 인스턴스 생성
    - `info(message, data?)`: 정보성 로그
    - `warn(message, data?)`: 경고 로그
    - `error(message, data?)`: 에러 로그

## 핵심 규칙
- 모든 로그는 JSON 문자열로 출력 (CloudWatch, Vercel Logs 등 파싱 용이성)
- 민감한 개인정보(비밀번호, 토큰 등)는 `data`에 포함하지 않음

## 테스트 명세
- `.spec/tests/unit/lib/logger.test.md` 참조
