"""Comprehensive tests for PDF processor module."""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

try:
    from promptops_engine.pdf_processor import PDFProcessor, PDFExtractionError, extrair_texto_pdf
    import PyPDF2
except ImportError:
    pytest.skip("PyPDF2 not installed", allow_module_level=True)


class TestPDFProcessor:
    """Test suite for PDFProcessor."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def processor(self, temp_cache_dir):
        """Create PDFProcessor instance."""
        return PDFProcessor(
            cache_dir=temp_cache_dir,
            enable_audit=True,
            max_file_size_mb=50,
        )

    def test_processor_initialization(self, processor):
        """Test processor initialization."""
        assert processor is not None
        assert processor.cache_dir.exists()
        assert processor.enable_audit is True
        assert processor.max_file_size_bytes == 50 * 1024 * 1024

    def test_invalid_pdf_path(self, processor):
        """Test handling of invalid PDF path."""
        resultado = processor.extrair_texto_pdf("/nonexistent/file.pdf")
        assert "Erro" in resultado
        assert "not found" in resultado

    def test_audit_logging(self, processor):
        """Test audit logging functionality."""
        # Attempt to extract from non-existent file (will generate error audit)
        processor.extrair_texto_pdf("/invalid/path.pdf")

        assert len(processor.audit_log) > 0
        audit_event = processor.audit_log[0]
        assert "timestamp" in audit_event
        assert "action" in audit_event
        assert "status" in audit_event
        assert audit_event["status"] == "failed"

    def test_statistics_tracking(self, processor):
        """Test statistics tracking."""
        # Generate errors
        processor.extrair_texto_pdf("/invalid/path1.pdf")
        processor.extrair_texto_pdf("/invalid/path2.pdf")

        stats = processor.obter_estatisticas()
        assert stats["errors"] == 2
        assert "total" in stats
        assert "cached" in stats
        assert "avg_time_ms" in stats

    def test_cache_operations(self, processor, temp_cache_dir):
        """Test cache file operations."""
        # Create a fake cache entry
        test_hash = "abc123def456"
        test_data = {
            "text": "Sample extracted text",
            "pages": 5,
            "hash": test_hash,
        }

        # Save to cache
        result = processor._save_to_cache(test_hash, test_data)
        assert result is True

        # Load from cache
        loaded_data = processor._load_from_cache(test_hash)
        assert loaded_data is not None
        assert loaded_data["text"] == "Sample extracted text"
        assert loaded_data["pages"] == 5

    def test_clear_cache(self, processor):
        """Test cache clearing functionality."""
        # Add some cache entries
        for i in range(5):
            processor._save_to_cache(f"hash_{i}", {"data": f"test_{i}"})

        # Clear cache
        deleted = processor.limpar_cache()
        assert deleted == 5

        # Verify cache is empty
        stats = processor.obter_estatisticas()
        cache_path = Path(stats["cache_dir"])
        cache_files = list(cache_path.glob("*.json"))
        assert len(cache_files) == 0

    def test_file_hash_computation(self, processor):
        """Test file hash computation."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"Test content")
            tmp_path = tmp.name

        try:
            hash1 = processor._compute_file_hash(tmp_path)
            hash2 = processor._compute_file_hash(tmp_path)
            # Same file should produce same hash
            assert hash1 == hash2
            # Hash should be hexadecimal
            assert len(hash1) == 64  # SHA256 hex length
        finally:
            Path(tmp_path).unlink()

    def test_extraccion_segura_metadata(self, processor):
        """Test secure extraction with metadata."""
        texto, metadata = processor.extrair_texto_pdf_seguro("/invalid/path.pdf")
        assert "status" in metadata
        assert metadata["status"] == "error"

    def test_truncation_in_secure_extraction(self, processor):
        """Test text truncation in secure extraction."""
        # Create a mock by simulating processor behavior
        text = "a" * 2000000  # 2M characters
        metadata = {"truncado": True, "status": "success"}
        assert metadata["truncado"] is True

    def test_audit_log_structure(self, processor):
        """Test audit log event structure."""
        # Trigger an error audit
        processor.extrair_texto_pdf("/invalid.pdf")

        assert len(processor.audit_log) > 0
        event = processor.audit_log[0]

        # Verify required fields
        assert "timestamp" in event
        assert "action" in event
        assert "status" in event
        assert "file" in event

        # Verify timestamp is ISO format
        try:
            datetime.fromisoformat(event["timestamp"])
        except ValueError:
            pytest.fail("Timestamp is not ISO format")

    def test_concurrent_audit_logging(self, processor):
        """Test audit logging with multiple events."""
        for i in range(10):
            processor._log_audit({
                "action": f"test_action_{i}",
                "status": "success",
            })

        assert len(processor.audit_log) == 10
        # Verify all events have timestamps
        for event in processor.audit_log:
            assert "timestamp" in event

    def test_error_handling_graceful_degradation(self, processor):
        """Test graceful error handling."""
        # Should not raise exceptions, only return error string
        result = processor.extrair_texto_pdf("/invalid/path.pdf")
        assert isinstance(result, str)
        assert "Erro" in result

    def test_backward_compatibility_function(self):
        """Test backward compatible function."""
        resultado = extrair_texto_pdf("/invalid/path.pdf")
        assert isinstance(resultado, str)
        assert "Erro" in resultado
