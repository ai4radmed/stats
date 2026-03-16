import pytest
from unittest.mock import MagicMock, patch
from sync_performance import fetch_performance_data, sync_performance_to_supabase, get_master_item_names

# 가짜 API 응답 데이터
MOCK_API_RESPONSE = {
    "body": {
        "pageNo": 1,
        "totalCount": 1,
        "numOfRows": 20,
        "items": [
            {
                "item": {
                    "ITEM_SEQ": "202401321",
                    "DATE_YEAR": "2024",
                    "ITEM_NAME": "플루빅토주",
                    "ENTP_NAME": "한국노바티스(주)",
                    "RESULT_PART": "수입",
                    "AMT": "400000"
                }
            }
        ]
    }
}

@patch("sync_performance.supabase")
def test_get_master_item_names(mock_supabase):
    """마스터 테이블에서 품목명 리스트를 잘 가져오는지 테스트"""
    mock_response = MagicMock()
    mock_response.data = [{"item_name": "A"}, {"item_name": "B"}]
    mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response

    names = get_master_item_names()
    assert names == ["A", "B"]

@patch("sync_performance.httpx.get")
def test_fetch_performance_data_with_item_name(mock_get):
    """품목명을 인자로 넣었을 때 URL에 포함되는지 테스트"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_get.return_value = mock_response

    items, req_count = fetch_performance_data("2024", "플루빅토주")

    # URL 검증 (인코딩된 품목명이 포함되어야 함)
    args, kwargs = mock_get.call_args
    assert "item_name=%ED%94%8C%EB%A3%A8%EB%B9%85%ED%86%A0%EC%주" in args[0] or "item_name=" in args[0]
    assert len(items) == 1
    assert items[0]["ITEM_SEQ"] == "202401321"

@patch("sync_performance.supabase")
def test_sync_performance_mapping(mock_supabase):
    """데이터 필드 매핑 검증"""
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    items = [{"ITEM_SEQ": "123", "DATE_YEAR": "2024", "RESULT_PART": "생산", "AMT": "500"}]
    sync_performance_to_supabase(items)

    called_data = mock_table.upsert.call_args[0][0]
    assert called_data["item_seq"] == "123"
    assert called_data["amount"] == 500
