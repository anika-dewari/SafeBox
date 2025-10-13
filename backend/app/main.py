from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import asyncio
from .metrics import collect_system_metrics, collect_cgroup_metrics
from .optimizer import Optimizer

app = FastAPI(title="SafeBox Backend", version="0.1.0")
optimizer = Optimizer()


@app.get("/api/v1/status")
async def status():
    sys_metrics = collect_system_metrics()
    cg_metrics = collect_cgroup_metrics("sandbox")
    # Create a simple utilization summary compatible with docs/snippets
    mem_current = cg_metrics.get("memory_current") or 0
    mem_max = cg_metrics.get("memory_max") or 0
    mem_ratio = (mem_current / mem_max) if (mem_current and mem_max) else 0.0

    cpu_cfg = cg_metrics.get("cpu_max") or {}
    quota = cpu_cfg.get("quota")
    period = cpu_cfg.get("period") or 100000
    cpu_limit_ratio = (quota / period) if (quota is not None and period) else None

    return JSONResponse({
        "system_load": sys_metrics.get("load"),
        "memory_info": sys_metrics.get("memory"),
        "cgroup": cg_metrics,
        "resource_utilization": {
            "memory_usage_ratio": mem_ratio,       # 0.0..1.0 of cgroup cap
            "cpu_limit_ratio": cpu_limit_ratio     # 0.0..1.0 of one full core equivalent
        }
    })


@app.websocket("/ws/metrics")
async def ws_metrics(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = {
                "system": collect_system_metrics(),
                "cgroup": collect_cgroup_metrics("sandbox")
            }
            await ws.send_json(data)
            await asyncio.sleep(1.0)
    except Exception:
        await ws.close()


@app.api_route("/api/v1/optimize", methods=["GET", "POST"])
async def optimize():
    recommendation = optimizer.compute_recommendation()
    optimizer.apply(recommendation)
    return JSONResponse({"applied": recommendation})


