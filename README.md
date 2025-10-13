# 🧠 SafeBox: Intelligent Resource Management & Deadlock Prevention System

> 🔒 **SafeBox** is a next-generation sandboxing system designed for secure process isolation, intelligent resource management, and proactive deadlock prevention using the **Banker’s Algorithm**.

---

## 🌟 Highlights

* ✨ **Secure Process Isolation** — Uses Linux **namespaces**, **cgroups**, and **seccomp filters** for robust sandboxing
* ⚙️ **Smart Resource Management** — Dynamically allocates and monitors CPU, memory, and I/O resources
* 🧮 **Deadlock Prevention** — Implements the proven **Banker’s Algorithm** for safe resource allocation
* 📊 **Real-Time Monitoring** — Interactive **CLI tools** and an optional **Flask-based dashboard**
* 🎓 **Built for Learning** — Ideal for **Operating Systems** coursework and academic research

---

## 🏗️ Core Components

| 🧩 Component            | ⚙️ Description                                                                 |
| ----------------------- | ------------------------------------------------------------------------------ |
| 🧱 **Sandbox Core**     | Provides secure process isolation using Linux namespaces and seccomp filters.  |
| ⚙️ **Resource Manager** | Monitors and enforces CPU, memory, and I/O usage for processes.                |
| 🧮 **Banker Engine**    | Implements the Banker’s Algorithm to prevent deadlocks and unsafe allocations. |
| 🧰 **Interface Layer**  | Command-line interface and Flask dashboard for real-time system monitoring.    |

---

## 🧾 Project Deliverables

| ✅ Deliverable                  | 📘 Description                                        |
| ------------------------------ | ----------------------------------------------------- |
| **Sandbox Core**               | Process isolation with namespaces and seccomp.        |
| **Resource Manager**           | CPU/memory monitoring and enforcement.                |
| **Banker’s Algorithm Engine**  | Ensures system remains in a safe state.               |
| **CLI + Flask Dashboard**      | User interfaces for administration and visualization. |
| **Unit Tests & Documentation** | Complete testing and academic documentation.          |

---

<p align="center">
  💡 *Developed with dedication by Team Ananta (B.Tech CSE, 3rd Year)* 💡
</p>

---

## 🚀 Getting Started (Developer)

> Note: Runtime features like Linux namespaces and cgroups require a Linux kernel (5.x+). You can develop on Windows using WSL2 or a Linux VM.

### 1) Project Layout

```
SafeBox/
  backend/               # FastAPI monitoring + optimization service
    app/
      main.py            # REST + WebSocket API
      metrics.py         # System + cgroup metrics collectors
      optimizer.py       # Feedback controller to tune cgroup limits
      cgroups_client.py  # Thin wrapper over the C++ CLI
    requirements.txt
  cgroup_agent/          # C++ cgroups v2 CLI (create, set limits, attach, stats)
    CMakeLists.txt
    src/cgroups.cpp
  scripts/
    build_agent.sh       # Build the C++ CLI via CMake
    run_backend.sh       # Launch FastAPI server
```

### 2) Prerequisites

- Linux kernel with cgroups v2 unified hierarchy enabled
- CMake ≥ 3.16 and a C++17 compiler
- Python ≥ 3.10

### 3) Build & Run

```bash
# Build C++ cgroup CLI
./scripts/build_agent.sh

# Create a sandbox cgroup example
sudo ./build/safebox_cgroup create sandbox
sudo ./build/safebox_cgroup mem.set sandbox 512M
sudo ./build/safebox_cgroup cpu.set sandbox 50000 100000  # 50% quota/period

# Install backend deps and start API (port 8000)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./../scripts/run_backend.sh
```

### 4) Try It

```bash
curl -s http://localhost:8000/api/v1/status | jq '.system_load, .memory_info'
```

### 4.1) Python virtual environment (.venv) setup

Use a project-local venv named `.venv` inside `backend/` to isolate Python dependencies.

1. Create venv (Ubuntu/WSL2)
```bash
cd backend
python3 -m venv .venv
```

2. Activate venv
```bash
source .venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the API
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. Deactivate when done
```bash
deactivate
```

6. Troubleshooting
- If the venv breaks (e.g., moved between Windows and WSL), recreate it:
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate && pip install -r requirements.txt
```
- The repo ignores `backend/.venv/` via `.gitignore`; never commit it.

### 5) Security Notes

- The CLI writes directly to `/sys/fs/cgroup` and generally requires root. Prefer invoking via controlled backend actions and least-privilege policies.

---

## 🧪 Scope of Ayush's Specialization

- Implement a minimal, robust cgroups v2 manager (create, limits, attach, stats)
- Real-time monitoring via REST + WebSocket streaming
- A simple performance optimizer that adjusts limits based on load