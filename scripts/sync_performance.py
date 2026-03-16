import os
import httpx
import logging
from datetime import datetime
from urllib.parse import quote
from dotenv import load_dotenv
from supabase import create_client, Client

# 로그 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

SUPABASE_URL = os.getenv("PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
MFDS_KEY = os.getenv("MFDS_SERVICE_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, MFDS_KEY]):
    logger.error("필수 환경 변수가 설정되지 않았습니다.")
    exit(1)

# Supabase 클라이언트 초기화
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 식약처 생산수입실적 API URL
PERFORMANCE_API_URL = "https://apis.data.go.kr/1471000/MdcinPrdctnImportAcmsltService02/getMdcinPrdctnImportrstList02"

def get_master_item_names():
    """마스터 테이블에서 모든 제품명을 가져옵니다."""
    try:
        response = supabase.table("mfds_radpharm_master").select("item_name").execute()
        return [row["item_name"] for row in response.data]
    except Exception as e:
        logger.error(f"마스터 아이템 로드 실패: {e}")
        return []

def fetch_performance_data(year: str, item_name: str = None):
    """특정 연도 및 품목의 생산수입실적 데이터를 수집합니다."""
    all_items = []
    page_no = 1
    num_of_rows = 100
    request_success_count = 0
    
    encoded_key = quote(MFDS_KEY)
    # 품목명이 있으면 인코딩하여 쿼리에 추가
    encoded_item_name = quote(item_name) if item_name else ""
    
    while True:
        # URL 수동 조립 (item_name 필터 추가)
        url = (
            f"{PERFORMANCE_API_URL}?serviceKey={encoded_key}"
            f"&pageNo={page_no}&numOfRows={num_of_rows}"
            f"&type=json&date_year={year}"
        )
        if item_name:
            url += f"&item_name={encoded_item_name}"
        
        try:
            logger.info(f"실적 API 호출: {item_name or '전체'} ({year}), Page {page_no}")
            response = httpx.get(url, timeout=30.0)
            
            if response.status_code == 401:
                logger.error("401 Unauthorized: API 키를 확인하세요.")
                break
                
            response.raise_for_status()
            request_success_count += 1
            data = response.json()
            
            body = data.get("body", {})
            items_envelopes = body.get("items", [])
            
            if not items_envelopes:
                break
                
            for env in items_envelopes:
                item = env.get("item")
                if item:
                    all_items.append(item)
            
            total_count = int(body.get("totalCount", 0))
            if page_no * num_of_rows >= total_count:
                break
                
            page_no += 1
            
        except Exception as e:
            logger.error(f"API 호출 중 오류 발생 ({item_name}): {e}")
            break
            
    return all_items, request_success_count

def sync_performance_to_supabase(items):
    """수집된 실적 데이터를 Supabase에 Upsert 합니다."""
    if not items:
        return 0

    success_count = 0
    for item in items:
        try:
            item_seq = item.get("ITEM_SEQ")
            if not item_seq:
                continue

            data = {
                "item_seq": str(item_seq),
                "year": str(item.get("DATE_YEAR")),
                "result_part": item.get("RESULT_PART"),
                "amount": int(item.get("AMT", 0)),
                "entp_name": item.get("ENTP_NAME"),
                "item_name": item.get("ITEM_NAME")
            }
            
            supabase.table("mfds_item_performance").upsert(data).execute()
            success_count += 1
            
        except Exception as e:
            logger.debug(f"저장 오류 ({item.get('ITEM_NAME')}): {e}")
            continue

    return success_count

def main():
    # 1. 마스터 아이템 리스트 확보
    master_items = get_master_item_names()
    if not master_items:
        logger.error("조회할 마스터 품목이 없습니다. 마스터 동기화를 먼저 진행하세요.")
        return

    logger.info(f"총 {len(master_items)}개의 품목에 대해 실적 조회를 시작합니다.")

    # 2. 최근 3개년 수집
    current_year = datetime.now().year
    years = [str(current_year), str(current_year - 1), str(current_year - 2)]
    
    total_items_saved = 0
    total_requests = 0
    
    for year in years:
        for item_name in master_items:
            items, req_count = fetch_performance_data(year, item_name)
            saved_count = sync_performance_to_supabase(items)
            
            total_items_saved += saved_count
            total_requests += req_count
            if saved_count > 0:
                logger.info(f"[{year}] {item_name}: {saved_count}건 저장 완료")

    # 3. 로그 기록
    try:
        supabase.table("api_sync_log").insert({
            "sync_source": "MFDS_PERFORMANCE_BY_ITEM",
            "request_count": total_requests,
            "item_count": total_items_saved,
            "status": "SUCCESS"
        }).execute()
        logger.info(f"동기화 완료: {total_requests} API calls, {total_items_saved} items saved.")
    except Exception as e:
        logger.error(f"로그 저장 실패: {e}")

if __name__ == "__main__":
    main()
