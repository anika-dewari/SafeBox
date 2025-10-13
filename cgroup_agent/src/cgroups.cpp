#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace fs = std::filesystem;

static const char* CG_BASE = "/sys/fs/cgroup";

static void usage() {
    std::cerr << "Usage:\n"
              << "  safebox_cgroup create <group>\n"
              << "  safebox_cgroup attach <group> <pid>\n"
              << "  safebox_cgroup mem.set <group> <bytes>\n"
              << "  safebox_cgroup cpu.set <group> <quota> <period>\n";
}

static bool write_file(const fs::path& p, const std::string& v) {
    try {
        std::ofstream f(p);
        f << v;
        return f.good();
    } catch (...) {
        return false;
    }
}

int main(int argc, char** argv) {
    if (argc < 3) { usage(); return 1; }
    std::string cmd = argv[1];
    std::string group = argv[2];
    fs::path base(CG_BASE);
    fs::path grp = base / group;

    if (cmd == "create") {
        try {
            fs::create_directories(grp);
            std::cout << "created: " << grp << "\n";
            return 0;
        } catch (const std::exception& e) {
            std::cerr << "create failed: " << e.what() << "\n";
            return 2;
        }
    }

    if (!fs::exists(grp)) {
        std::cerr << "group does not exist: " << grp << "\n";
        return 3;
    }

    if (cmd == "attach") {
        if (argc < 4) { usage(); return 1; }
        std::string pid = argv[3];
        if (!write_file(grp / "cgroup.procs", pid + "\n")) {
            std::cerr << "failed to attach pid" << "\n";
            return 4;
        }
        std::cout << "attached pid " << pid << " to " << group << "\n";
        return 0;
    }

    if (cmd == "mem.set") {
        if (argc < 4) { usage(); return 1; }
        std::string bytes = argv[3];
        if (!write_file(grp / "memory.max", bytes + "\n")) {
            std::cerr << "failed to set memory.max" << "\n";
            return 5;
        }
        std::cout << "memory.max=" << bytes << " for " << group << "\n";
        return 0;
    }

    if (cmd == "cpu.set") {
        if (argc < 5) { usage(); return 1; }
        std::string quota = argv[3];
        std::string period = argv[4];
        if (!write_file(grp / "cpu.max", quota + " " + period + "\n")) {
            std::cerr << "failed to set cpu.max" << "\n";
            return 6;
        }
        std::cout << "cpu.max=" << quota << "/" << period << " for " << group << "\n";
        return 0;
    }

    usage();
    return 1;
}


