import subprocess
from typing import Sequence


class CgroupClient:
    def __init__(self, binary_path: str = "../build/safebox_cgroup") -> None:
        self.binary_path = binary_path

    def _run(self, args: Sequence[str]) -> None:
        subprocess.run([self.binary_path, *args], check=False)

    def create(self, group: str) -> None:
        self._run(["create", group])

    def attach_pid(self, group: str, pid: int) -> None:
        self._run(["attach", group, str(pid)])

    def set_memory_max(self, group: str, bytes_limit: int) -> None:
        self._run(["mem.set", group, str(bytes_limit)])

    def set_cpu_max(self, group: str, quota: int, period: int) -> None:
        self._run(["cpu.set", group, str(quota), str(period)])


