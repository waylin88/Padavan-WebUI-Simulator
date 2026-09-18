"""快速检查模拟器的核心 HTTP 链路。"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from web_simulator.sim import app


def main():
    client = app.test_client()

    response = client.get("/Login.asp")
    assert response.status_code == 200

    response = client.post(
        "/Login.asp",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data.lower()

    response = client.get("/state.js")
    assert response.status_code == 200
    assert response.mimetype == "application/javascript"
    assert b"menuL1" in response.data

    response = client.get("/jquery.js")
    assert response.status_code == 200
    assert response.mimetype == "application/javascript"
    assert b"jQuery" in response.data

    response = client.get("/update.cgi?output=sysinfo")
    assert response.status_code == 200
    assert response.mimetype == "application/json"

    print("Padavan WebUI simulator smoke test passed")


if __name__ == "__main__":
    main()
