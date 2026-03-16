from unittest.mock import MagicMock, patch
import pytest
import xml.etree.ElementTree as ET
from sync_clinical_trials import parse_date, fetch_clinical_trials

def test_parse_date():
    assert parse_date("20240316") == "2024-03-16"
    assert parse_date("2024031") is None
    assert parse_date(None) is None
    assert parse_date("") is None

def test_xml_parsing_logic():
    # API 응답 모킹용 XML
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <response>
        <header>
            <resultCode>00</resultCode>
            <resultMsg>NORMAL SERVICE.</resultMsg>
        </header>
        <body>
            <numOfRows>10</numOfRows>
            <pageNo>1</pageNo>
            <totalCount>1</totalCount>
            <items>
                <item>
                    <APPLY_ENTP_NAME>서울대학교병원</APPLY_ENTP_NAME>
                    <APPROVAL_TIME>20240101</APPROVAL_TIME>
                    <LAB_NAME>서울대학교병원</LAB_NAME>
                    <GOODS_NAME>177Lu-Test</GOODS_NAME>
                    <CLINIC_EXAM_TITLE>테스트 임상시험</CLINIC_EXAM_TITLE>
                    <CLINIC_STEP_NAME>3상</CLINIC_STEP_NAME>
                    <CLINIC_TEST_SN>20240001</CLINIC_TEST_SN>
                </item>
            </items>
        </body>
    </response>
    """
    
    with patch("httpx.get") as mock_get:
        # httpx.get 모킹
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = sample_xml.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        results = fetch_clinical_trials("177Lu")
        
        assert len(results) == 1
        assert results[0]["clinic_test_sn"] == "20240001"
        assert results[0]["goods_name"] == "177Lu-Test"
        assert results[0]["approval_time"] == "2024-01-01"
        assert results[0]["clinic_step_name"] == "3상"
