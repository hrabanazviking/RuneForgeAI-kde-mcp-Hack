#!/usr/bin/env python3
"""yrsa-kde.py — one-shot kde-mcp driver.

Usage: yrsa-kde.py TOOL [JSON_ARGS] [--save-image PATH]

Spawns kde-mcp --mode=live (stdio), runs ONE tool, prints a compact result.
Image content is saved to a file (default /tmp/yrsa-kde-shot.png) instead of
being dumped as base64 into the terminal. Installed 2026-11-19.
"""
import base64, json, os, subprocess, sys, threading, time

def main():
    argv = sys.argv[1:]
    if not argv:
        print("usage: yrsa-kde.py TOOL [JSON_ARGS] [--save-image PATH]", file=sys.stderr)
        return 2
    tool = argv[0]
    args = {}
    save_image = "/tmp/yrsa-kde-shot.png"
    rest = argv[1:]
    i = 0
    while i < len(rest):
        if rest[i] == "--save-image" and i + 1 < len(rest):
            save_image = rest[i + 1]
            i += 2
        else:
            args = json.loads(rest[i])
            i += 1

    env = dict(os.environ)
    env.update({
        "XDG_RUNTIME_DIR": "/run/user/1000",
        "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
        "WAYLAND_DISPLAY": "wayland-0",
        "DISPLAY": ":0",
        "XDG_CURRENT_DESKTOP": "KDE",
        "XDG_SESSION_TYPE": "wayland",
    })
    p = subprocess.Popen(["/home/volmarr/.local/bin/kde-mcp", "--mode=live"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, env=env, text=True)
    responses = {}

    def reader():
        for line in p.stdout:
            try:
                msg = json.loads(line)
            except Exception:
                continue
            if "id" in msg:
                responses[msg["id"]] = msg

    threading.Thread(target=reader, daemon=True).start()

    def send(obj):
        p.stdin.write(json.dumps(obj) + "\n")
        p.stdin.flush()

    def call(id_, method, params):
        send({"jsonrpc": "2.0", "id": id_, "method": method, "params": params})
        for _ in range(200):
            if id_ in responses:
                return responses[id_]
            time.sleep(0.2)
        return {}

    r = call(1, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                               "clientInfo": {"name": "yrsa-kde", "version": "1.0"}})
    if "result" not in r:
        print("kde-mcp initialize failed:", json.dumps(r)[:300])
        p.kill()
        return 1
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    r = call(2, "tools/call", {"name": tool, "arguments": args})
    p.kill()
    res = r.get("result", {})
    if "error" in r:
        print("ERROR:", json.dumps(r["error"])[:500])
        return 1
    out = []
    for c in res.get("content", []):
        if c.get("type") == "image":
            raw = base64.b64decode(c.get("data", ""))
            with open(save_image, "wb") as f:
                f.write(raw)
            out.append("[image saved: %s (%d bytes, %s)]" % (save_image, len(raw), c.get("mimeType")))
        elif c.get("type") == "text":
            out.append(c.get("text", ""))
    text = "\n".join(out)
    print(text[:4000])
    if res.get("isError"):
        print("[tool reported isError]")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
