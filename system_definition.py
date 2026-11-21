import platform


def get_system_info(to_macos=True, convert_arch=True) -> tuple[str, str]:
    # windows, linux, darwin (macos)
    os_name = platform.system().lower()

    # windows: x86_64, amd64 (чаще amd64 чем x86_64), x86, i386, i686
    # linux: x86_64, arm64, x86, i386, i686
    # macos: x86_64, arm64, aarch64 (M1, M2...)
    arch = platform.machine().lower()

    if os_name == "darwin" and to_macos:
        os_name = "macos"

    arch_aliases = {
        "amd64": "x64",
        "x86_64": "x64",
        "x86": "x86",
        "i386": "x86",
        "i686": "x86",
        "arm64": "arm64",
        "aarch64": "arm64"
    }

    arch = arch_aliases.get(arch) if convert_arch else arch

    return (os_name, arch)