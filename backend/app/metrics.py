import os
import platform
import psutil


def collect_system_metrics() -> dict:
    load = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
    vm = psutil.virtual_memory()
    cpu = psutil.cpu_times_percent(interval=None)
    return {
        "platform": platform.platform(),
        "load": {"1m": load[0], "5m": load[1], "15m": load[2]},
        "memory": {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "percent": vm.percent,
        },
        "cpu_percent": psutil.cpu_percent(interval=None),
        "cpu_times_percent": cpu._asdict(),
    }


def collect_cgroup_metrics(group_name: str) -> dict:
    # Read a subset of common cgroup v2 stats if available
    base = "/sys/fs/cgroup/" + group_name
    metrics = {"group": group_name, "present": os.path.exists(base)}
    if not metrics["present"]:
        return metrics

    def read_int(path: str) -> int | None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                v = f.read().strip()
                return int(v)
        except Exception:
            return None

    def read_kv(path: str) -> dict:
        data = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2 and parts[1].isdigit():
                        data[parts[0]] = int(parts[1])
        except Exception:
            pass
        return data

    metrics["memory_current"] = read_int(os.path.join(base, "memory.current"))
    metrics["memory_max"] = read_int(os.path.join(base, "memory.max"))
    metrics["cpu_max"] = None
    try:
        with open(os.path.join(base, "cpu.max"), "r", encoding="utf-8") as f:
            quota, period = f.read().strip().split()
            metrics["cpu_max"] = {
                "quota": None if quota == "max" else int(quota),
                "period": int(period),
            }
    except Exception:
        pass

    metrics["memory_stats"] = read_kv(os.path.join(base, "memory.stat"))
    metrics["io_stats"] = read_kv(os.path.join(base, "io.stat"))
    return metrics


