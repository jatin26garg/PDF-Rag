import pytest
import asyncio
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.services.rag_service import RAGService

client = TestClient(app)

# ===================================================
# TEST 1: Health Check
# ===================================================

def test_health_check():
    """Verify the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "rag-tool" in str(response.json())  # Tool endpoints registered

# ===================================================
# TEST 2: Document Upload
# ===================================================

def test_upload_document():
    """Test uploading a document."""
    
    # Create a test text file
    test_content = """
    Company Vacation Policy
    
    All employees receive 15 days of paid vacation per year.
    Vacation requests must be approved by the manager.
    """
    
    # Save to temp file
    test_file = Path(tempfile.gettempdir()) / "test_doc.txt"
    test_file.write_text(test_content)
    
    # Upload
    with open(test_file, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test_doc.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "document_id" in data
    assert data["filename"] == "test_doc.txt"
    
    # Clean up
    test_file.unlink()
    
    return data["document_id"]

# ===================================================
# TEST 3: Query
# ===================================================

def test_query():
    """Test asking a question."""
    
    # First upload a document
    doc_id = test_upload_document()
    
    # Then query
    response = client.post(
        "/query",
        json={"question": "How many vacation days do I get?", "top_k": 3}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0
    
    # Verify answer contains relevant info
    answer = data["answer"].lower()
    assert "15" in answer or "vacation" in answer

# ===================================================
# TEST 5: Document Listing
# ===================================================

def test_list_documents():
    """Test listing all documents."""
    
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# ===================================================
# TEST 6: Delete Document
# ===================================================

def test_delete_document():
    """Test deleting a document."""
    
    # Upload a document
    doc_id = test_upload_document()
    
    # Delete it
    response = client.delete(f"/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify it's gone
    response = client.get("/documents")
    docs = response.json()
    assert not any(d["id"] == doc_id for d in docs)

# ===================================================
# TEST 7: Invalid File Type
# ===================================================

def test_invalid_file_type():
    """Test uploading an invalid file type."""
    
    # Create a fake .exe file
    test_file = Path(tempfile.gettempdir()) / "test.exe"
    test_file.write_text("fake executable")
    
    with open(test_file, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test.exe", f, "application/x-msdownload")}
        )
    
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]
    
    test_file.unlink()

# ===================================================
# TEST 8: Empty Query
# ===================================================

def test_empty_query():
    """Test asking an empty question."""
    
    response = client.post(
        "/query",
        json={"question": "", "top_k": 3}
    )
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()