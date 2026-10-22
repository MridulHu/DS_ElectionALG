
import socket, threading, json, time
from datetime import datetime

ID = 1
NODES = range(1, 6)
PORT = lambda n: 5000 + n

leader = 0
lock = threading.Lock()
ok = threading.Event()
coordinator = threading.Event()
running = False


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] Node {ID}: {msg}", flush=True)


def send(n, kind):
    try:
        with socket.create_connection(("127.0.0.1", PORT(n)), 1) as s:
            s.sendall((json.dumps({"type": kind, "id": ID}) + "\n").encode())
        log(f"SEND {kind} -> Node {n}")
        return True
    except OSError:
        return False


def election():
    global running
    with lock:
        if running:
            return
        running = True
    threading.Thread(target=run_election, daemon=True).start()


def run_election():
    global leader, running
    try:
        while True:
            ok.clear()
            coordinator.clear()
            higher = [n for n in NODES if n > ID]

            log("Starting election")
            for n in higher:
                send(n, "ELECTION")

            if not higher or not ok.wait(2):
                with lock:
                    leader = ID
                log(f"I am the leader: {ID}")
                for n in NODES:
                    if n != ID:
                        send(n, "COORDINATOR")
                return

            if coordinator.wait(3):
                return
            log("Coordinator timeout; retrying")
    finally:
        with lock:
            running = False


def handle(c):
    global leader
    with c:
        try:
            m = json.loads(c.makefile().readline())
            kind, sender = m["type"], int(m["id"])
            log(f"RECV {kind} <- Node {sender}")

            if kind == "ELECTION":
                send(sender, "OK")
                election()

            elif kind == "OK":
                ok.set()

            elif kind == "COORDINATOR":
                with lock:
                    leader = sender
                coordinator.set()
                log(f"Leader is Node {sender}")

            elif kind == "PING":
                c.sendall((json.dumps({"type": "OK", "id": ID}) + "\n").encode())
        except (OSError, ValueError, KeyError):
            pass


def server():
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", PORT(ID)))
        s.listen()
        log(f"Listening on port {PORT(ID)}")

        while True:
            c, _ = s.accept()
            threading.Thread(target=handle, args=(c,), daemon=True).start()


def ping(n):
    try:
        with socket.create_connection(("127.0.0.1", PORT(n)), 1) as s:
            s.settimeout(1)
            s.sendall((json.dumps({"type": "PING", "id": ID}) + "\n").encode())
            return json.loads(s.makefile().readline())["type"] == "OK"
    except (OSError, ValueError, KeyError):
        return False


threading.Thread(target=server, daemon=True).start()
time.sleep(0.5)
election()

while True:
    time.sleep(2)
    with lock:
        current = leader
    if current and current != ID and not ping(current):
        with lock:
            if leader == current:
                leader = 0
        log(f"Leader Node {current} failed")
        election()
