"""Enterprise-grade PDF extraction module with caching and error handling.

Features:
    - Robust PDF text extraction
    - In-memory and disk caching
    - Comprehensive error handling
    - Audit logging integration
    - Performance metrics
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
from functools import lru_cache

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors."""
    pass


class PDFProcessor:
    """Enterprise PDF processing with caching and audit trails."""

    def __init__(
        self,
        cache_dir: str = ".cache/pdf",
        enable_audit: bool = True,
        max_file_size_mb: int = 100,
    ):
        """Initialize PDF processor.

        Args:
            cache_dir: Directory for caching extracted text
            enable_audit: Enable audit logging
            max_file_size_mb: Maximum PDF file size in MB
        """
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required. Install with: pip install PyPDF2")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.enable_audit = enable_audit
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.audit_log: list = []
        self._extraction_stats = {"total": 0, "cached": 0, "errors": 0, "avg_time_ms": 0}

    def _compute_file_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Hexadecimal hash string
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _get_cache_path(self, file_hash: str) -> Path:
        """Get cache file path for given hash.

        Args:
            file_hash: File hash

        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{file_hash}.json"

    def _load_from_cache(self, file_hash: str) -> Optional[Dict]:
        """Load extracted text from cache.

        Args:
            file_hash: File hash

        Returns:
            Cached data or None if not found
        """
        cache_path = self._get_cache_path(file_hash)
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Cache read error: {e}")
                return None
        return None

    def _save_to_cache(self, file_hash: str, data: Dict) -> bool:
        """Save extracted text to cache.

        Args:
            file_hash: File hash
            data: Data to cache

        Returns:
            True if successful
        """
        cache_path = self._get_cache_path(file_hash)
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            logger.error(f"Cache write error: {e}")
            return False

    def _log_audit(self, event: Dict) -> None:
        """Log audit event.

        Args:
            event: Event details
        """
        if not self.enable_audit:
            return

        event["timestamp"] = datetime.now().isoformat()
        self.audit_log.append(event)
        logger.info(f"PDF Audit: {event}")

    def extrair_texto_pdf(self, caminho_pdf: str) -> str:
        """Extract text from PDF file (senior-grade implementation).

        Args:
            caminho_pdf: Path to PDF file

        Returns:
            Extracted text or error message

        Raises:
            PDFExtractionError: On extraction failure
        """
        import time

        start_time = time.time()
        texto_completo = ""

        try:
            # Validate file exists
            if not os.path.exists(caminho_pdf):
                raise PDFExtractionError(f"PDF file not found: {caminho_pdf}")

            # Validate file size
            file_size = os.path.getsize(caminho_pdf)
            if file_size > self.max_file_size_bytes:
                raise PDFExtractionError(
                    f"PDF file too large: {file_size / 1024 / 1024:.2f}MB "
                    f"(max: {self.max_file_size_bytes / 1024 / 1024:.2f}MB)"
                )

            # Check cache
            file_hash = self._compute_file_hash(caminho_pdf)
            cached_data = self._load_from_cache(file_hash)
            if cached_data:
                self._extraction_stats["cached"] += 1
                self._log_audit({
                    "action": "extract_pdf_cached",
                    "file": caminho_pdf,
                    "hash": file_hash,
                    "pages": cached_data["pages"],
                    "status": "success",
                })
                logger.info(f"PDF loaded from cache: {caminho_pdf}")
                return cached_data["text"]

            # Extract from PDF
            with open(caminho_pdf, "rb") as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                num_pages = len(leitor.pages)

                for pagina in range(num_pages):
                    try:
                        texto_completo += leitor.pages[pagina].extract_text()
                    except Exception as e:
                        logger.warning(f"Error extracting page {pagina}: {e}")
                        continue

            if not texto_completo:
                raise PDFExtractionError("No text extracted from PDF")

            # Cache result
            cache_data = {
                "text": texto_completo,
                "pages": num_pages,
                "hash": file_hash,
                "extracted_at": datetime.now().isoformat(),
            }
            self._save_to_cache(file_hash, cache_data)

            # Update stats
            elapsed_ms = (time.time() - start_time) * 1000
            self._extraction_stats["total"] += 1
            total_time = (
                self._extraction_stats["avg_time_ms"]
                * (self._extraction_stats["total"] - 1)
                + elapsed_ms
            ) / self._extraction_stats["total"]
            self._extraction_stats["avg_time_ms"] = total_time

            # Audit log
            self._log_audit({
                "action": "extract_pdf",
                "file": caminho_pdf,
                "pages": num_pages,
                "char_count": len(texto_completo),
                "elapsed_ms": elapsed_ms,
                "status": "success",
            })

            logger.info(
                f"PDF extracted successfully: {caminho_pdf} "
                f"({num_pages} pages, {len(texto_completo)} chars, {elapsed_ms:.2f}ms)"
            )
            return texto_completo

        except PDFExtractionError as e:
            self._extraction_stats["errors"] += 1
            self._log_audit({
                "action": "extract_pdf_error",
                "file": caminho_pdf,
                "error": str(e),
                "status": "failed",
            })
            logger.error(f"PDF extraction error: {e}")
            return f"Erro ao ler PDF: {str(e)}"

        except Exception as e:
            self._extraction_stats["errors"] += 1
            self._log_audit({
                "action": "extract_pdf_error",
                "file": caminho_pdf,
                "error": str(e),
                "exception_type": type(e).__name__,
                "status": "failed",
            })
            logger.error(f"Unexpected PDF extraction error: {e}", exc_info=True)
            return f"Erro inesperado ao ler PDF: {str(e)}"

    def extrair_texto_pdf_seguro(
        self, caminho_pdf: str, tamanho_maximo_caracteres: int = 1000000
    ) -> Tuple[str, Dict]:
        """Extract text with security validation and metadata.

        Args:
            caminho_pdf: Path to PDF
            tamanho_maximo_caracteres: Maximum characters to extract

        Returns:
            Tuple of (extracted_text, metadata)
        """
        texto = self.extrair_texto_pdf(caminho_pdf)

        if texto.startswith("Erro"):
            return texto, {"status": "error", "error": texto}

        if len(texto) > tamanho_maximo_caracteres:
            texto = texto[:tamanho_maximo_caracteres]
            truncado = True
        else:
            truncado = False

        metadata = {
            "status": "success",
            "char_count": len(texto),
            "truncado": truncado,
            "file": caminho_pdf,
        }

        return texto, metadata

    def obter_estatisticas(self) -> Dict:
        """Get extraction statistics.

        Returns:
            Statistics dictionary
        """
        return {
            **self._extraction_stats,
            "cache_dir": str(self.cache_dir),
            "audit_events": len(self.audit_log),
        }

    def limpar_cache(self) -> int:
        """Clear all cached extractions.

        Returns:
            Number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except OSError as e:
                logger.warning(f"Failed to delete cache file: {e}")
        logger.info(f"Cache cleared: {count} files deleted")
        return count


# Convenience function for backward compatibility
def extrair_texto_pdf(caminho_pdf: str) -> str:
    """Extract text from PDF file (backward compatible).

    Args:
        caminho_pdf: Path to PDF file

    Returns:
        Extracted text or error message
    """
    processor = PDFProcessor(enable_audit=True)
    return processor.extrair_texto_pdf(caminho_pdf)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    processor = PDFProcessor(enable_audit=True)

    # Extract from PDF
    # texto = processor.extrair_texto_pdf("manual_slc.pdf")
    # print(texto[:500])

    # Extract with security validation
    # texto, metadata = processor.extrair_texto_pdf_seguro("manual_slc.pdf")
    # print(json.dumps(metadata, indent=2))

    # Get statistics
    # print(json.dumps(processor.obter_estatisticas(), indent=2))
