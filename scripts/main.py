import os
import httpx
import logging
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

# 식약처 API URL (Service07 버전 확인됨)
MFDS_API_URL = "https://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService07/getDrugPrdtPrmsnDtlInq06"

from urllib.parse import quote

def fetch_mfds_data(atc_code: str):
    """식약처 데이터를 수집합니다. (Full URL 방식으로 인코딩 우회)"""
    all_items = []
    page_no = 1
    num_of_rows = 100
    
    # .env의 키가 디코딩된 상태이므로 URL 전송을 위해 인코딩
    encoded_key = quote(MFDS_KEY)
    
    while True:
        # 이중 인코딩을 방지하기 위해 URL을 수동으로 조립
        url = (
            f"{MFDS_API_URL}?serviceKey={encoded_key}"
            f"&pageNo={page_no}&numOfRows={num_of_rows}"
            f"&type=json&atc_code={atc_code}"
        )
        
        try:
            logger.info(f"MFDS API 호출: {atc_code}, Page {page_no}")
            # params 인자를 사용하지 않고 수동 조립된 url만 전달
            response = httpx.get(url, timeout=30.0)
            
            if response.status_code == 401:
                logger.error("401 Unauthorized: API 키 인코딩 또는 활성화 상태를 확인하세요.")
                break
            elif response.status_code == 500:
                logger.error("500 Internal Server Error: API 서버 일시적 오류")
                break

            response.raise_for_status()
            data = response.json()
            
            body = data.get("body", {})
            items = body.get("items", [])
            
            if not items:
                break
                
            all_items.extend(items)
            logger.info(f"Page {page_no}: {len(items)}개 수집됨 (누적: {len(all_items)})")
            
            total_count = int(body.get("totalCount", 0))
            if page_no * num_of_rows >= total_count:
                break
                
            page_no += 1
            
        except Exception as e:
            logger.error(f"API 호출 중 오류 발생: {e}")
            break
            
    return all_items

def classify_category(item_name: str):
    """제품명 기반 카테고리 분류"""
    if any(keyword in item_name for keyword in ["제너레이터", "발생기", "Generator"]):
        return "Generator"
    elif any(keyword in item_name.lower() for keyword in ["키트", "kit"]):
        return "Cold Kit"
    else:
        return "Finished"

def sync_to_supabase(items):
    """수집된 데이터를 Supabase에 Upsert 합니다."""
    if not items:
        logger.warning("저장할 데이터가 없습니다.")
        return

    for item in items:
        try:
            item_name = item.get("ITEM_NAME", "")
            data = {
                "item_seq": str(item.get("ITEM_SEQ")),
                "item_name": item_name,
                "entp_name": item.get("ENTP_NAME"),
                "atc_code": item.get("ATC_CODE"),
                "category": classify_category(item_name),
                "edi_code": item.get("EDI_CODE"),
                "main_item_ingr": item.get("MAIN_ITEM_INGR"),
                "item_permit_date": item.get("ITEM_PERMIT_DATE") or None,
                "cancel_date": item.get("CANCEL_DATE") or None,
                "item_class_no": item.get("CLASS_NO"),
            }
            
            supabase.table("mfds_radpharm_master").upsert(data).execute()
            logger.info(f"저장 완료: {item_name}")
            
        except Exception as e:
            logger.error(f"데이터 저장 중 오류 발생 ({item.get('ITEM_NAME')}): {e}")

def main():
    atc_codes = ["V09", "V10"]
    
    for code in atc_codes:
        logger.info(f"--- ATC {code} 수집 시작 ---")
        items = fetch_mfds_data(code)
        logger.info(f"수집된 항목 수: {len(items)}")
        sync_to_supabase(items)

if __name__ == "__main__":
    main()
