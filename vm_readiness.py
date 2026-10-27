"""VM Migration Readiness Checker — v1."""

CHECKS = (
    "os_supported",
    "network_configured",
    "required_packages_installed",
)


def check_vm_readiness(vm):
    """Evaluate whether a VM is ready for migration.

    Args:
        vm: Dict with vm_name (str) and three boolean readiness fields.
            Missing check keys are treated as failures (NOT_READY).
            Invalid types raise TypeError or ValueError.

    Returns:
        Dict with vm_name, passed, failed, and status ("READY" or "NOT_READY").
    """
    if not isinstance(vm, dict):
        raise TypeError(f"vm must be a dict, got {type(vm).__name__}")

    vm_name = vm.get("vm_name")
    if not isinstance(vm_name, str) or not vm_name.strip():
        raise ValueError("vm_name must be a non-empty string")

    passed = []
    failed = []

    for check in CHECKS:
        if check not in vm:
            failed.append(check)
            continue

        value = vm[check]
        if not isinstance(value, bool):
            raise TypeError(
                f"{check} must be a bool, got {type(value).__name__}"
            )

        if value:
            passed.append(check)
        else:
            failed.append(check)

    status = "READY" if not failed else "NOT_READY"

    return {
        "vm_name": vm_name,
        "passed": passed,
        "failed": failed,
        "status": status,
    }


if __name__ == "__main__":
    ready_vm = {
        "vm_name": "web-app-01",
        "os_supported": True,
        "network_configured": True,
        "required_packages_installed": True,
    }

    not_ready_vm = {
        "vm_name": "legacy-db-02",
        "os_supported": True,
        "network_configured": False,
        "required_packages_installed": False,
    }

    for label, vm in (("Ready VM", ready_vm), ("Not-ready VM", not_ready_vm)):
        result = check_vm_readiness(vm)
        print(f"{label}: {result['vm_name']}")
        print(f"  status: {result['status']}")
        print(f"  passed: {result['passed']}")
        print(f"  failed: {result['failed']}")
        print()
