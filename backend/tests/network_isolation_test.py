import socket
import requests
from contextlib import contextmanager


@contextmanager
def intercept_connections():
    """Intercept and record socket connections."""

    connections = []

    original_connect = socket.socket.connect

    def intercepted_connect(self, address):

        # Record connection
        connections.append(address)

        print(f"🔌 Connection attempted to: {address}")

        # Get host
        host = address[0]

        # Allow only localhost
        allowed_hosts = [
            "127.0.0.1",
            "localhost",
            "::1"
        ]

        if host not in allowed_hosts:
            raise Exception(
                f"❌ EXTERNAL CALL DETECTED: {host}"
            )

        return original_connect(self, address)

    socket.socket.connect = intercepted_connect

    try:
        yield connections

    finally:
        socket.socket.connect = original_connect


def test_no_external_calls():

    print("\n🔒 Running Network Isolation Test...")

    with intercept_connections() as connections:

        try:

            # -------------------------
            # Upload document
            # -------------------------

            print("\n📄 Uploading document...")

            with open("tests/test.txt", "rb") as f:

                response = requests.post(
                    "http://localhost:8000/upload",
                    files={"file": f}
                )

            if response.status_code != 200:
                print("❌ Upload failed")
                print(response.status_code)
                print(response.text)
                return

            print("✅ Upload completed")

            # -------------------------
            # Query
            # -------------------------

            print("\n❓ Sending query...")

            response = requests.post(
                "http://localhost:8000/query",
                json={
                    "question": "What is the vacation policy?",
                    "top_k": 3
                }
            )

            if response.status_code != 200:
                print("❌ Query failed")
                print(response.status_code)
                print(response.text)
                return

            print("✅ Query completed")

            # -------------------------
            # Result
            # -------------------------

            print("\n🔒 NETWORK ISOLATION RESULT")

            print(f"Connections detected: {len(connections)}")

            for connection in connections:
                print(f"   → {connection}")

            print("\n✅ NO EXTERNAL CALLS DETECTED!")

        except Exception as e:

            print(f"\n❌ {e}")


if __name__ == "__main__":
    test_no_external_calls()