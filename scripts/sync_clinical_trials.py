import os
import httpx
import logging
import xml.etree.ElementTree as ET
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

# 식약처 API URL
CLINICAL_API_URL = "https://apis.data.go.kr/1471000/MdcincLincTestInfoService02/getMdcincLincTestInfoList02"

def parse_date(date_str: str):
    """YYYYMMDD 형식을 YYYY-MM-DD 형식으로 변환"""
    if not date_str or len(date_str) != 8:
        return None
    try:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    except:
        return None

def fetch_clinical_trials(goods_name: str):
    """식약처 임상시험 정보를 수집합니다."""
    all_items = []
    page_no = 1
    num_of_rows = 100
    encoded_key = quote(MFDS_KEY)
    
    while True:
        url = (
            f"{CLINICAL_API_URL}?serviceKey={encoded_key}"
            f"&pageNo={page_no}&numOfRows={num_of_rows}"
            f"&goods_name={quote(goods_name)}"
        )
        
        try:
            logger.info(f"MFDS 임상시험 API 호출: {goods_name}, Page {page_no}")
            response = httpx.get(url, timeout=30.0)
            response.raise_for_status()
            
            # 응답 파싱 (XML 우선)
            root = ET.fromstring(response.content)
            
            # 헤더 체크
            header = root.find("header")
            if header is not None:
                result_code = header.findtext("resultCode")
                if result_code != "00":
                    result_msg = header.findtext("resultMsg")
                    logger.error(f"API 에러: {result_code} - {result_msg}")
                    break

            body = root.find("body")
            if body is None:
                break
                
            items_node = body.find("items")
            if items_node is None:
                break
                
            items = items_node.findall("item")
            if not items:
                break
                
            for item in items:
                item_data = {
                    "clinic_test_sn": item.findtext("CLINIC_TEST_SN"),
                    "goods_name": item.findtext("GOODS_NAME"),
                    "entp_name": item.findtext("APPLY_ENTP_NAME"),
                    "approval_time": parse_date(item.findtext("APPROVAL_TIME")),
                    "clinic_exam_title": item.findtext("CLINIC_EXAM_TITLE"),
                    "clinic_step_name": item.findtext("CLINIC_STEP_NAME"),
                    "lab_name": item.findtext("LAB_NAME"),
                }
                all_items.append(item_data)
            
            logger.info(f"Page {page_no}: {len(items)}개 추출됨 (누적: {len(all_items)})")
            
            total_count = int(body.findtext("totalCount") or 0)
            if page_no * num_of_rows >= total_count:
                break
                
            page_no += 1
            
        except ET.ParseError as e:
            logger.error(f"XML 파싱 오류: {e}")
            break
        except Exception as e:
            logger.error(f"API 호출 중 오류 발생: {e}")
            break
            
    return all_items

def sync_to_supabase(items):
    """수집된 데이터를 Supabase에 Upsert 합니다."""
    if not items:
        logger.warning("저장할 데이터가 없습니다.")
        return

    success_count = 0
    for item in items:
        try:
            # 필수 값 체크
            if not item["clinic_test_sn"]:
                continue
                
            supabase.table("mfds_clinical_trials").upsert(item).execute()
            success_count += 1
            logger.debug(f"저장 완료: {item['goods_name']} ({item['clinic_test_sn']})")
            
        except Exception as e:
            logger.error(f"데이터 저장 중 오류 발생 ({item.get('clinic_test_sn')}): {e}")

    logger.info(f"총 {success_count}개의 임상시험 데이터 동기화 완료.")

def main():
    target_keywords = ["177Lu", "Lutathera", "루타테라"]
    
    for keyword in target_keywords:
        logger.info(f"--- '{keyword}' 관련 임상시험 수집 시작 ---")
        items = fetch_clinical_trials(keyword)
        sync_to_supabase(items)

if __name__ == "__main__":
    main()
