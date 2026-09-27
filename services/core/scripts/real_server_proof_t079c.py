"""T-079c Part E, item 6 — REAL-server proof (uvicorn, actual port).

Mounts the production-style app the same way main.py does (FastAPI +
BodyLimitMiddleware + the onboarding router with a BOUND server scope,
so the routes are reachable) and drives it over a real TCP socket:

1. /health
2. the three POST routes with real multipart/JSON bodies
3. an over-limit JSON body with an honest Content-Length  -> 413
4. an over-limit body with NO Content-Length (chunked)     -> 413

Run from services/core:  python scripts/real_server_proof_t079c.py
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CORE))

from app.onboarding.page import (  # noqa: E402
    DevEscapes,
    OnboardingPageStore,
    create_onboarding_router,
)

SERVER = (CORE / "scripts" / "_t079c_server.py").resolve()
MAX_FILE = 500_000


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main() -> int:
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "--port", str(port),
         "--log-level", "warning", "scripts._t079c_server:app"],
        cwd=str(CORE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(2.0)
    ok = True
    try:
        import httpx
        with httpx.Client(
            base_url=f"http://127.0.0.1:{port}", timeout=30
        ) as c:
            print("health:", c.get("/health").status_code)
            r0 = c.post("/onboarding/page/sessions")
            print("POST /onboarding/page/sessions      ->", r0.status_code)
            sid = r0.json()["session_id"]
            ra = c.post(f"/onboarding/page/sessions/{sid}/answer",
                        json={"text": "สุภาพ"})
            print("POST .../answer (json)              ->", ra.status_code)
            rf = c.post(f"/onboarding/page/sessions/{sid}/file",
                        files={"file": ("m.csv", b"a,1\nb,2\n", "text/csv")})
            print("POST .../file (multipart)           ->", rf.status_code)
            rw = c.post(f"/onboarding/page/sessions/{sid}/website",
                        json={"url": "https://jea-ma.example/menu"})
            print("POST .../website (json)             ->", rw.status_code)

            big = b"y" * (MAX_FILE * 2 + 1)
            ro = c.post(f"/onboarding/page/sessions/{sid}/answer",
                        content=big,
                        headers={"content-type": "application/json"})
            print("OVERSIZE json, honest CL            ->", ro.status_code)

            # GENUINE chunked request, on the wire: a raw socket hand-writes
            # the chunked framing itself — NO content-length header exists
            # anywhere on the wire — several small chunk lines, a
            # terminating zero-size chunk, then read the status line.
            # httpx would add content-length, so this goes lower.
            import string
            printable = string.printable.encode()
            body = (printable * ((MAX_FILE * 2 + 1) // len(printable) + 1))[:MAX_FILE * 2 + 1]
            with socket.create_connection(("127.0.0.1", port), timeout=30) as s:
                n_chunks = 32          # ~31 KiB each, provably NOT one blob
                per = (len(body) + n_chunks - 1) // n_chunks
                wire = b"POST /onboarding/page/sessions/%s/answer HTTP/1.1\r\n" % sid.encode()
                wire += b"Host: t\r\nContent-Type: application/json\r\n"
                wire += b"Transfer-Encoding: chunked\r\n\r\n"
                for i in range(n_chunks):
                    piece = body[i * per:(i + 1) * per]
                    wire += b"%x\r\n" % len(piece) + piece + b"\r\n"
                wire += b"0\r\n\r\n"
                assert b"content-length" not in wire.lower()
                s.sendall(wire)
                status = b""
                while b"\r\n" not in status:
                    status += s.recv(4096)
                code = int(status.split()[1])
                print("OVERSIZE raw-socket chunked, no CL", "->", code)
            statuses = [ro.status_code, code]
            ok = (ra.status_code == 200 and rf.status_code == 200
                  and statuses == [413, 413])
            # chunked oversize case must also be a clean 413
            print("RESULT:", "PASS" if ok else "FAIL")
    finally:
        proc.terminate()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
