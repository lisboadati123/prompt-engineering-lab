# 📄 PDF Processing Module Documentation

## Overview

The `pdf_processor.py` module provides enterprise-grade PDF text extraction with:
- **Intelligent Caching**: SHA256-based caching to avoid re-processing identical PDFs
- **Audit Trails**: Complete logging of all extraction operations
- **Error Handling**: Graceful error handling with detailed messages
- **Performance Metrics**: Real-time statistics and performance tracking
- **Security Validation**: File size and content validation

## Installation

```bash
pip install PyPDF2
```

## Quick Start

### Basic Usage (Backward Compatible)

```python
from promptops_engine.pdf_processor import extrair_texto_pdf

# Simple extraction
texto = extrair_texto_pdf("manual_slc.pdf")
print(texto[:500])  # First 500 characters
```

### Professional Usage

```python
from promptops_engine.pdf_processor import PDFProcessor
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize processor
processor = PDFProcessor(
    cache_dir=".cache/pdf",
    enable_audit=True,
    max_file_size_mb=100
)

# Extract text
texto = processor.extrair_texto_pdf("manual_slc.pdf")
if not texto.startswith("Erro"):
    print(f"Extracted: {len(texto)} characters from 5 pages")
```

## API Reference

### PDFProcessor Class

#### Constructor

```python
PDFProcessor(
    cache_dir: str = ".cache/pdf",
    enable_audit: bool = True,
    max_file_size_mb: int = 100
)
```

**Parameters:**
- `cache_dir`: Directory for caching extracted content (default: `.cache/pdf`)
- `enable_audit`: Enable/disable audit logging (default: `True`)
- `max_file_size_mb`: Maximum PDF size in MB (default: `100`)

#### Methods

##### `extrair_texto_pdf(caminho_pdf: str) -> str`

Extract text from a PDF file with caching.

```python
texto = processor.extrair_texto_pdf("document.pdf")
```

**Returns:** Extracted text or error message string

**Features:**
- Automatic caching based on file hash
- Comprehensive error handling
- Audit logging
- Performance tracking

---

##### `extrair_texto_pdf_seguro(caminho_pdf: str, tamanho_maximo_caracteres: int = 1000000) -> Tuple[str, Dict]`

Extract text with security validation and metadata.

```python
texto, metadata = processor.extrair_texto_pdf_seguro(
    "document.pdf",
    tamanho_maximo_caracteres=500000
)

if metadata["status"] == "success":
    print(f"Extracted {metadata['char_count']} characters")
    if metadata["truncado"]:
        print("Text was truncated due to size limit")
```

**Returns:** Tuple of (extracted_text, metadata_dict)

**Metadata fields:**
- `status`: "success" or "error"
- `char_count`: Number of characters extracted
- `truncado`: Boolean indicating if text was truncated
- `file`: Source file path
- `error`: Error message (if status is "error")

---

##### `obter_estatisticas() -> Dict`

Get extraction statistics.

```python
stats = processor.obter_estatisticas()
print(f"Total extractions: {stats['total']}")
print(f"From cache: {stats['cached']}")
print(f"Errors: {stats['errors']}")
print(f"Avg time: {stats['avg_time_ms']:.2f}ms")
```

**Returns:**
```json
{
  "total": 15,
  "cached": 8,
  "errors": 2,
  "avg_time_ms": 145.3,
  "cache_dir": ".cache/pdf",
  "audit_events": 45
}
```

---

##### `limpar_cache() -> int`

Clear all cached extractions.

```python
deleted = processor.limpar_cache()
print(f"Deleted {deleted} cache files")
```

**Returns:** Number of cache files deleted

---

## Audit Logging

When `enable_audit=True`, all operations are logged with timestamps and details.

### Audit Log Structure

```python
{
  "timestamp": "2026-05-06T10:30:45.123456",
  "action": "extract_pdf",  # or "extract_pdf_cached", "extract_pdf_error"
  "file": "document.pdf",
  "pages": 5,
  "char_count": 15234,
  "elapsed_ms": 245.3,
  "status": "success"  # or "failed"
}
```

### Accessing Audit Logs

```python
for event in processor.audit_log:
    print(f"[{event['timestamp']}] {event['action']}: {event['status']}")
    if event['status'] == 'failed':
        print(f"  Error: {event['error']}")
```

## Caching System

### How It Works

1. PDF file is processed with SHA256 hash
2. Hash is used as cache key
3. Extracted text is stored in `{cache_dir}/{hash}.json`
4. Subsequent extractions from same file use cache (instant retrieval)

### Cache File Structure

```json
{
  "text": "Extracted PDF content...",
  "pages": 5,
  "hash": "a1b2c3d4...",
  "extracted_at": "2026-05-06T10:30:45.123456"
}
```

### Cache Management

```python
# Clear all cache
processor.limpar_cache()

# Get cache statistics
stats = processor.obter_estatisticas()
print(f"Cache directory: {stats['cache_dir']}")
```

## Error Handling

### Common Error Scenarios

#### File Not Found
```python
texto = processor.extrair_texto_pdf("/invalid/path.pdf")
# Returns: "Erro ao ler PDF: PDF file not found: /invalid/path.pdf"
```

#### File Too Large
```python
# If max_file_size_mb=100 and file is 150MB
texto = processor.extrair_texto_pdf("large.pdf")
# Returns: "Erro ao ler PDF: PDF file too large: 150.25MB (max: 100.00MB)"
```

#### Corrupted PDF
```python
texto = processor.extrair_texto_pdf("corrupted.pdf")
# Returns: "Erro ao ler PDF: [error details]"
```

### Error Handling Best Practices

```python
texto = processor.extrair_texto_pdf("document.pdf")

if texto.startswith("Erro"):
    # Handle error
    logger.error(f"PDF extraction failed: {texto}")
    # Use cached version or skip
else:
    # Process extracted text
    # Integrate with NLP pipeline
    pass
```

## Integration with PromptOps Pipeline

### Extracting PDF for LLM Processing

```python
from promptops_engine import PromptOpsEngine
from promptops_engine.pdf_processor import PDFProcessor

# 1. Extract PDF
pdf_processor = PDFProcessor(enable_audit=True)
texto_pdf = pdf_processor.extrair_texto_pdf("manual.pdf")

# 2. Validate extraction
if texto_pdf.startswith("Erro"):
    print(f"Failed to extract PDF: {texto_pdf}")
else:
    # 3. Send to PromptOps pipeline
    engine = PromptOpsEngine(enable_guardrails=True)
    resultado = engine.execute(
        user_input=f"Analise o seguinte documento:\n{texto_pdf[:5000]}",
        usuario_id="doc_analyzer_001"
    )
    print(resultado)
```

## Performance Benchmarks

### Typical Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| First extraction (5 pages) | ~200-300ms | Depends on PDF complexity |
| Cached retrieval | ~5-10ms | From disk cache |
| Hash computation (10MB PDF) | ~50-100ms | SHA256 |
| Statistics calculation | <1ms | In-memory |

### Performance Optimization Tips

```python
# 1. Use cache for repeated documents
processor = PDFProcessor(enable_audit=True)  # Cache enabled by default

# 2. Limit file size
processor_small = PDFProcessor(max_file_size_mb=20)  # Smaller files

# 3. Disable audit for high throughput
processor_fast = PDFProcessor(enable_audit=False)  # No logging overhead
```

## Testing

### Run PDF Processor Tests

```bash
pytest tests/test_pdf_processor.py -v
```

### Test Coverage

- ✅ File not found handling
- ✅ Cache operations (save/load)
- ✅ Audit logging
- ✅ Statistics tracking
- ✅ File hash computation
- ✅ Error handling
- ✅ Backward compatibility

## Troubleshooting

### Q: PyPDF2 not installed

```bash
pip install PyPDF2
```

### Q: Cache not working

1. Verify cache directory is writable:
   ```bash
   ls -la .cache/pdf/
   ```

2. Check disk space:
   ```bash
   df -h
   ```

3. Enable debug logging:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

### Q: Slow extraction

- Check file size (use `max_file_size_mb` parameter)
- Enable caching (default enabled)
- Check system resources (CPU, RAM)
- Consider splitting large PDFs

## See Also

- [PromptOps Engine](./docs/API.md)
- [Security Module](./docs/SECURITY.md)
- [Audit Logging](./docs/AUDIT_LOGGING.md)
