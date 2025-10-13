from .metrics import collect_system_metrics, collect_cgroup_metrics
from .cgroups_client import CgroupClient


class Optimizer:
    def __init__(self, group_name: str = "sandbox") -> None:
        self.group_name = group_name
        self.client = CgroupClient()

    def compute_recommendation(self) -> dict:
        sys_m = collect_system_metrics()
        cg_m = collect_cgroup_metrics(self.group_name)

        mem_used = cg_m.get("memory_current") or 0
        mem_max = cg_m.get("memory_max") or 0

        recommendation: dict = {"group": self.group_name}

        # Simple policy: if memory usage > 80% of cap, raise by 20%, else if < 40%, lower by 10%
        if mem_max and mem_used:
            ratio = mem_used / max(1, mem_max)
            if ratio > 0.8:
                recommendation["memory.max"] = int(mem_max * 1.2)
            elif ratio < 0.4:
                recommendation["memory.max"] = int(mem_max * 0.9)

        # CPU: if system load 1m > logical cores, increase to 80%; else 50%
        cpu_target_quota = None
        load1 = sys_m.get("load", {}).get("1m", 0.0)
        try:
            import psutil

            cores = psutil.cpu_count(logical=True) or 1
        except Exception:
            cores = 1
        busy = load1 > cores
        period = 100000
        if busy:
            cpu_target_quota = int(0.8 * period)
        else:
            cpu_target_quota = int(0.5 * period)
        recommendation["cpu.max"] = {"quota": cpu_target_quota, "period": period}

        return recommendation

    def apply(self, plan: dict) -> None:
        mem = plan.get("memory.max")
        if mem is not None:
            self.client.set_memory_max(self.group_name, mem)

        cpu = plan.get("cpu.max")
        if isinstance(cpu, dict) and cpu.get("quota") is not None:
            self.client.set_cpu_max(self.group_name, int(cpu["quota"]), int(cpu["period"]))


