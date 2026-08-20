import os
import sys

# Set path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from google import genai
from app.core.exceptions import QuotaExhaustedError
from app.core.llm_client import generate_content_with_fallback, ConfigurationError
from app.ai.intelligence.parser import SituationParser
from app.ai.reasoning.generator import ResponseGenerator
from app.ai.intelligence.document_parser import MultimodalDocumentParser
from app.schemas.contracts import Situation
from app.rag.retrieval.models import EvidencePack
from app.ai.policy.action_policy import PolicyDirectives

class TestFallbackLogic(unittest.TestCase):
    def setUp(self):
        self.mock_sleep = patch('time.sleep').start()
        
        # Patch config settings
        self.patcher_primary = patch('app.core.llm_client.settings.gemini_api_key', 'primary_key')
        self.patcher_backup = patch('app.core.llm_client.settings.gemini_api_key_backup', 'backup_key')
        self.patcher_primary.start()
        self.patcher_backup.start()
        
        # Patch the genai.Client
        self.client_patcher = patch('app.core.llm_client.genai.Client')
        self.MockClientClass = self.client_patcher.start()
        
        # Keep track of clients created
        self.primary_mock = MagicMock()
        self.backup_mock = MagicMock()
        
        def side_effect(api_key):
            if api_key == 'primary_key':
                return self.primary_mock
            elif api_key == 'backup_key':
                return self.backup_mock
            return MagicMock()
            
        self.MockClientClass.side_effect = side_effect

    def tearDown(self):
        patch.stopall()

    def test_1_primary_success(self):
        self.primary_mock.models.generate_content.return_value = "success"
        res = generate_content_with_fallback("model", ["test"])
        self.assertEqual(res, "success")
        self.assertEqual(self.primary_mock.models.generate_content.call_count, 1)
        self.assertEqual(self.backup_mock.models.generate_content.call_count, 0)

    def test_2_primary_transient_429_then_success(self):
        self.primary_mock.models.generate_content.side_effect = [
            Exception("429 Too Many Requests"),
            Exception("429 Too Many Requests"),
            "success"
        ]
        res = generate_content_with_fallback("model", ["test"])
        self.assertEqual(res, "success")
        self.assertEqual(self.primary_mock.models.generate_content.call_count, 3)
        self.assertEqual(self.backup_mock.models.generate_content.call_count, 0)

    def test_3_primary_503_then_success(self):
        self.primary_mock.models.generate_content.side_effect = [
            Exception("503 Service Unavailable"),
            "success"
        ]
        res = generate_content_with_fallback("model", ["test"])
        self.assertEqual(res, "success")
        self.assertEqual(self.primary_mock.models.generate_content.call_count, 2)
        self.assertEqual(self.backup_mock.models.generate_content.call_count, 0)

    def test_4_primary_quota_exhausted_backup_success(self):
        self.primary_mock.models.generate_content.side_effect = Exception("429 Quota Exceeded")
        self.backup_mock.models.generate_content.return_value = "backup_success"
        
        res = generate_content_with_fallback("model", ["test"])
        
        self.assertEqual(res, "backup_success")
        self.assertEqual(self.primary_mock.models.generate_content.call_count, 1)
        self.assertEqual(self.backup_mock.models.generate_content.call_count, 1)

    def test_5_primary_quota_exhausted_backup_quota_exhausted(self):
        self.primary_mock.models.generate_content.side_effect = Exception("429 limit reached")
        self.backup_mock.models.generate_content.side_effect = Exception("429 Resource Exhausted")
        
        with self.assertRaises(QuotaExhaustedError):
            generate_content_with_fallback("model", ["test"])
            
        self.assertEqual(self.primary_mock.models.generate_content.call_count, 1)
        self.assertEqual(self.backup_mock.models.generate_content.call_count, 1)

    @patch('app.core.llm_client.settings.gemini_api_key_backup', '')
    def test_6_no_backup_configured(self):
        self.primary_mock.models.generate_content.side_effect = Exception("429 quota reached")
        
        with self.assertRaises(QuotaExhaustedError):
            generate_content_with_fallback("model", ["test"])
            
        self.assertEqual(self.primary_mock.models.generate_content.call_count, 1)
        self.assertEqual(self.backup_mock.models.generate_content.call_count, 0)

    def test_7_backup_invalid_auth(self):
        self.primary_mock.models.generate_content.side_effect = Exception("429 quota reached")
        self.backup_mock.models.generate_content.side_effect = Exception("403 Permission Denied")
        
        with self.assertRaises(ConfigurationError):
            generate_content_with_fallback("model", ["test"])
            
        self.assertEqual(self.primary_mock.models.generate_content.call_count, 1)
        self.assertEqual(self.backup_mock.models.generate_content.call_count, 1)

    def test_8_mock_error_429(self):
        with self.assertRaises(QuotaExhaustedError):
            generate_content_with_fallback("model", ["test"], mock_input="MOCK_ERROR_429")
            
        self.assertEqual(self.primary_mock.models.generate_content.call_count, 0)
        self.assertEqual(self.backup_mock.models.generate_content.call_count, 0)

    def test_9_document_parser_fallback(self):
        with patch('app.ai.intelligence.document_parser.genai.Client') as mock_genai:
            mock_client = MagicMock()
            mock_genai.return_value = mock_client
            
            with patch('app.core.llm_client.generate_content_with_fallback') as mock_fallback:
                mock_response = MagicMock()
                mock_response.parsed = MagicMock()
                mock_response.parsed.claims = []
                mock_fallback.return_value = mock_response
                
                parser = MultimodalDocumentParser()
                parser.api_key = "test"
                # Mock the fitz open since we just want to test if generate_content_with_fallback is called
                res = parser._extract_with_gemini("test text", "doc1", is_image=False)
                
                self.assertEqual(res, [])
                mock_fallback.assert_called_once()

    def test_10_generator_fallback(self):
        with patch('app.core.llm_client.generate_content_with_fallback') as mock_fallback:
            mock_response = MagicMock()
            mock_response.parsed = MagicMock()
            mock_response.parsed.model_dump.return_value = {
                "situation_summary": "sum", "clarification_questions": [], "verified_information": [],
                "source_citations": [], "evidence_checklist": [], "action_plan": [], 
                "legal_aid_resources": [], "legal_aid_status": "NOT_RELEVANT", "disclaimer": ""
            }
            mock_fallback.return_value = mock_response
            
            generator = ResponseGenerator()
            generator.api_key = "test"
            sit = Situation(category="C", subcategory="S", facts=[], parties=[])
            ep = EvidencePack(chunks=[], sufficiency_state="SUFFICIENT", reason="test")
            pol = PolicyDirectives()
            pol.allow_specific_actions = True
            pol.allow_definitive_claims = False
            pol.mandatory_caveat = "x"
            
            res = generator.generate(sit, ep, pol)
            self.assertEqual(res.situation_summary, "sum")
            mock_fallback.assert_called_once()

    def test_11_parser_fallback(self):
         with patch('app.core.llm_client.generate_content_with_fallback') as mock_fallback:
            mock_response = MagicMock()
            mock_response.parsed = Situation(category="C", subcategory="S", facts=[], parties=[])
            mock_fallback.return_value = mock_response
            
            parser = SituationParser()
            parser.api_key = "test"
            res = parser.parse("hello")
            
            self.assertEqual(res.category, "C")
            mock_fallback.assert_called_once()

if __name__ == '__main__':
    unittest.main(verbosity=2)
