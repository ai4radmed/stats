# 로그 시스템 가이드

## 개요

nmstats는 운영 중 문제를 신속하게 발견하고 대응하기 위해 구조화된 JSON 로그 시스템을 사용합니다. 모든 로그는 `src/lib/logger.ts`를 통해 출력되어야 합니다.

## 로그 레벨 설정

### 환경변수 설정

`.env` 파일의 `PUBLIC_LOG_LEVEL` 변수로 제어하며, 운영 환경(`production`)에서는 `error` 또는 `warn` 설정을 권장합니다.

```env
PUBLIC_LOG_LEVEL=debug   # 상세 개발 로그 포함
PUBLIC_LOG_LEVEL=info    # 정상 동작 기록 (기본값)
PUBLIC_LOG_LEVEL=warn    # 잠재적 문제
PUBLIC_LOG_LEVEL=error   # 실제 오류
```

### 로그 레벨 우선순위

| 레벨    | 우선순위 | 용도           |
| ------- | -------- | -------------- |
| `debug` | 0        | 개발 상세 정보 |
| `info`  | 1        | 정상 동작 기록 |
| `warn`  | 2        | 잠재적 문제    |
| `error` | 3        | 실제 오류      |

---

## 로그 포맷 (Standard JSON)

모든 로그는 일관된 JSON 형식으로 출력되어 파싱 및 분석을 용이하게 합니다.

```json
{
    "level": "error",
    "module": "api-client",
    "message": "데이터 가져오기 실패",
    "data": {
        "errorCode": "FETCH_FAILED",
        "details": "..."
    },
    "timestamp": "2026-03-12T07:10:00.000Z"
}
```

### 필드 설명

- `level`: 로그 레벨 (`debug`, `info`, `warn`, `error`)
- `module`: 로그 발생 모듈/컴포넌트명
- `message`: 로그 요약 메시지
- `data`: 추가 컨텍스트 정보 (민감정보 제외 필수)
- `timestamp`: ISO 8601 타임스탬프

---

## 보안 지침

1. **민감 정보 노출 금지**: 비밀번호, API 키, 개인식별정보(PII), 인증 토큰 등은 절대 로그의 `data` 필드에 포함해서는 안 됩니다.
2. **에러 객체 필터링**: `Error` 객체를 그대로 `JSON.stringify` 할 경우 구조가 노출될 수 있으므로, 에러 메시지(`error.message`) 위주로 기록합니다.
3. **운영 환경 레벨 제어**: 라이브 서비스에서는 `info` 이하의 로그가 대량 발생하여 비용 상승 및 성능 저하를 초래할 수 있으므로 주의합니다.

---

## 참고 코드
- 로거 유틸리티: `src/lib/logger.ts`
- 로거 명세: `.spec/src/lib/logger.md`
