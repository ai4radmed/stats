import pytest
from unittest.mock import MagicMock, patch
from main import classify_category, sync_to_supabase

# 1. 카테고리 분류 로직 테스트
def test_classify_category():
    assert classify_category("99Mo/99mTc 제너레이터") == "Generator"
    assert classify_category("테크네슘 MDP 키트") == "Cold Kit"
    assert classify_category("Techne Kit 10mg") == "Cold Kit"
    assert classify_category("18F-FDG 주사액") == "Finished"
    assert classify_category("일반 방사성의약품") == "Finished"

# 2. Supabase 적재 로직 테스트 (Mock)
@patch("main.supabase")
def test_sync_to_supabase_mapping(mock_supabase):
    # Mock 설정
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    test_items = [
        {
            "ITEM_SEQ": 20240001,
            "ITEM_NAME": "테스트 제너레이터",
            "ENTP_NAME": "대한핵의학",
            "ATC_CODE": "V09CA02",
            "EDI_CODE": "FB011"
        }
    ]
    
    # 실행
    sync_to_supabase(test_items)
    
    # 검증: upsert가 호출되었는가?
    mock_table.upsert.assert_called()
    
    # 검증: 데이터가 snake_case로 올바르게 매핑되었는가?
    args, _ = mock_table.upsert.call_args
    upsert_data = args[0]
    
    assert upsert_data["item_seq"] == "20240001"  # 문자열 형변환 확인
    assert upsert_data["item_name"] == "테스트 제너레이터"
    assert upsert_data["category"] == "Generator"

# 3. 빈 데이터 처리 테스트
def test_sync_to_supabase_empty():
    with patch("main.logger") as mock_logger:
        sync_to_supabase([])
        mock_logger.warning.assert_called_with("저장할 데이터가 없습니다.")

if __name__ == "__main__":
    pytest.main()
