import time
import requests


BASE_URL = "http://localhost:8000"
FILE_PATH = "tests/test.txt"


def measure_performance():
    """Measure end-to-end RAG performance."""

    # -----------------------------------------
    # 1. Upload document
    # -----------------------------------------
    print("Uploading document...")

    start = time.time()

    with open(FILE_PATH, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/upload",
            files={"file": f}
        )

    upload_time = time.time() - start

    # Check upload response
    if response.status_code != 200:
        print("❌ Upload failed")
        print("Status:", response.status_code)
        print("Response:", response.text)
        return

    data = response.json()

    doc_id = data["document_id"]

    print(f"✅ Upload successful")
    print(f"Document ID: {doc_id}")


    # -----------------------------------------
    # 2. Query RAG
    # -----------------------------------------
    print("\nAsking question...")

    start = time.time()

    response = requests.post(
        f"{BASE_URL}/query",
        json={
            "question": "What is the vacation policy?",
            "top_k": 3
        }
    )

    query_time = time.time() - start


    # Check query response
    if response.status_code != 200:
        print("❌ Query failed")
        print("Status:", response.status_code)
        print("Response:", response.text)
        return

    result = response.json()

    print("✅ Query successful")


    # -----------------------------------------
    # 3. Print answer
    # -----------------------------------------

    print("\nAnswer:")
    print(result)


    # -----------------------------------------
    # 4. Performance report
    # -----------------------------------------

    print("""
═══════════════════════════════════════════
           PERFORMANCE REPORT
═══════════════════════════════════════════
""")

    print(f"Upload time: {upload_time:.2f}s")
    print(f"Query time:  {query_time:.2f}s")
    print(f"Total time:  {upload_time + query_time:.2f}s")

    if query_time < 20:
        print("Status: ✅ PASS")
    else:
        print("Status: ⚠️ SLOW")

    print("═══════════════════════════════════════════")


if __name__ == "__main__":
    measure_performance()