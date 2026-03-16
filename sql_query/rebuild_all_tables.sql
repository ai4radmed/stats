-- ==========================================
-- nmstats 전체 테이블 초기화 및 재빌드
-- (주의: 이 스크립트를 실행하면 기존 데이터가 삭제될 수 있습니다.)
-- ==========================================

-- 1. 사용자 프로필 테이블 (profiles)
-- AUTH.USERS와 연동되는 기본 프로필 테이블
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. 방사성의약품 품목허가 마스터 테이블 (mfds_radpharm_master)
-- 식약처 OpenAPI 데이터를 수집하여 저장하는 기준 테이블
CREATE TABLE IF NOT EXISTS public.mfds_radpharm_master (
    item_seq TEXT PRIMARY KEY,                       -- 품목기준코드 (식약처 고유 ID)
    item_name TEXT NOT NULL,                         -- 제품명 (한글)
    entp_name TEXT NOT NULL,                         -- 업체명
    atc_code TEXT,                                   -- ATC 분류 코드 (V09, V10 등)
    category TEXT,                                   -- 항목 유형 (Generator, Kit, Finished)
    edi_code TEXT,                                   -- 건강보험심사평가원 EDI 코드
    main_item_ingr TEXT,                             -- 제품의 주요 유효 성분
    item_permit_date DATE,                           -- 최초 품목 허가 일자
    cancel_date DATE,                                -- 허가 취소 또는 만료 일자
    item_class_no TEXT,                              -- 식약처 분류번호 (예: 431)
    created_at TIMESTAMPTZ DEFAULT now(),             -- 데이터 생성 시각
    updated_at TIMESTAMPTZ DEFAULT now()              -- 데이터 최종 수정 시각
);

-- 인덱스 생성 (조회 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_mfds_radpharm_atc ON public.mfds_radpharm_master(atc_code);
CREATE INDEX IF NOT EXISTS idx_mfds_radpharm_edi ON public.mfds_radpharm_master(edi_code);

-- updated_at 자동 업데이트를 위한 트리거 함수
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 설정
DROP TRIGGER IF EXISTS tr_mfds_radpharm_update ON public.mfds_radpharm_master;
CREATE TRIGGER tr_mfds_radpharm_update
    BEFORE UPDATE ON public.mfds_radpharm_master
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- 3. API 동기화 로그 테이블 (api_sync_log)
-- 데이터 수집 파이프라인의 상태 및 통계를 기록
CREATE TABLE IF NOT EXISTS public.api_sync_log (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    sync_source TEXT NOT NULL,                        -- 수집 출처 (예: MFDS)
    request_count INTEGER DEFAULT 0,                  -- API 호출 횟수
    item_count INTEGER DEFAULT 0,                     -- 수집된 데이터 수
    status TEXT,                                      -- 상태 (SUCCESS, FAIL)
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS 정책 설정 (기본적으로 모두 거부 후 필요한 권한만 부여)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mfds_radpharm_master ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_sync_log ENABLE ROW LEVEL SECURITY;

-- 공통: 누구나 읽기 가능 (Select)
DROP POLICY IF EXISTS "Allow public read access" ON public.mfds_radpharm_master;
CREATE POLICY "Allow public read access" ON public.mfds_radpharm_master
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read sync logs" ON public.api_sync_log;
CREATE POLICY "Allow public read sync logs" ON public.api_sync_log
    FOR SELECT USING (true);

-- 4. 품목별 연도별 생산/수입 실적 테이블 (mfds_item_performance)
-- 식약처 생산/수입 실적 데이터를 저장
CREATE TABLE IF NOT EXISTS public.mfds_item_performance (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    item_seq TEXT REFERENCES public.mfds_radpharm_master(item_seq) ON DELETE CASCADE,
    year TEXT NOT NULL,                               -- 실적 연도 (DATE_YEAR)
    result_part TEXT NOT NULL,                        -- 실적 구분 (RESULT_PART: 생산/수입)
    amount BIGINT DEFAULT 0,                          -- 실적 금액 (AMT)
    entp_name TEXT,                                   -- 업체명 (ENTP_NAME)
    item_name TEXT,                                   -- 제품명 (ITEM_NAME)
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    -- 유니크 제약 조건: 동일 품목의 연도별 실적 구분 데이터 중복 방지
    UNIQUE(item_seq, year, result_part)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_performance_item_seq ON public.mfds_item_performance(item_seq);
CREATE INDEX IF NOT EXISTS idx_performance_year ON public.mfds_item_performance(year);

-- 트리거 설정 (updated_at)
DROP TRIGGER IF EXISTS tr_mfds_performance_update ON public.mfds_item_performance;
CREATE TRIGGER tr_mfds_performance_update
    BEFORE UPDATE ON public.mfds_item_performance
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- RLS 정책 설정
ALTER TABLE public.mfds_item_performance ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public read performance" ON public.mfds_item_performance;
CREATE POLICY "Allow public read performance" ON public.mfds_item_performance
    FOR SELECT USING (true);

-- 관리자만 삽입/수정/삭제 가능 (나중에 프로필 기반 admin 정책 필요)
-- 5. 의약품 임상시험 정보 테이블 (mfds_clinical_trials)
-- 식약처 OpenAPI를 통해 수집된 임상시험 상세 정보
CREATE TABLE IF NOT EXISTS public.mfds_clinical_trials (
    clinic_test_sn TEXT PRIMARY KEY,                  -- 임상시험 일련번호 (고유 키)
    goods_name TEXT NOT NULL,                         -- 제품명
    entp_name TEXT,                                   -- 신청인(업체명)
    approval_time DATE,                               -- 승인일자
    clinic_exam_title TEXT,                           -- 임상시험 제목
    clinic_step_name TEXT,                            -- 임상시험 단계 (1상, 2상, 3상 등)
    lab_name TEXT,                                    -- 실시기관
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_clinical_goods_name ON public.mfds_clinical_trials(goods_name);

-- 트리거 설정 (updated_at)
DROP TRIGGER IF EXISTS tr_mfds_clinical_update ON public.mfds_clinical_trials;
CREATE TRIGGER tr_mfds_clinical_update
    BEFORE UPDATE ON public.mfds_clinical_trials
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- RLS 정책 설정
ALTER TABLE public.mfds_clinical_trials ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public read clinical trials" ON public.mfds_clinical_trials;
CREATE POLICY "Allow public read clinical trials" ON public.mfds_clinical_trials
    FOR SELECT USING (true);
