"""Unit tests for check_vm_readiness."""

import copy
import unittest

from vm_readiness import CHECKS, check_vm_readiness


def make_vm(**overrides):
    """Build a valid ready VM, optionally overriding fields."""
    vm = {
        "vm_name": "test-vm",
        "os_supported": True,
        "network_configured": True,
        "required_packages_installed": True,
    }
    vm.update(overrides)
    return vm


class CheckVmReadinessTests(unittest.TestCase):
    def test_all_checks_pass_returns_ready(self):
        result = check_vm_readiness(make_vm())

        self.assertEqual(result["vm_name"], "test-vm")
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["passed"], list(CHECKS))
        self.assertEqual(result["failed"], [])

    def test_partial_failure_returns_not_ready(self):
        result = check_vm_readiness(make_vm(network_configured=False))

        self.assertEqual(result["status"], "NOT_READY")
        self.assertEqual(
            result["passed"],
            ["os_supported", "required_packages_installed"],
        )
        self.assertEqual(result["failed"], ["network_configured"])

    def test_all_checks_fail(self):
        result = check_vm_readiness(
            make_vm(
                os_supported=False,
                network_configured=False,
                required_packages_installed=False,
            )
        )

        self.assertEqual(result["status"], "NOT_READY")
        self.assertEqual(result["passed"], [])
        self.assertEqual(result["failed"], list(CHECKS))

    def test_missing_check_key_counts_as_failed(self):
        vm = make_vm()
        del vm["required_packages_installed"]

        result = check_vm_readiness(vm)

        self.assertEqual(result["status"], "NOT_READY")
        self.assertIn("required_packages_installed", result["failed"])
        self.assertNotIn("required_packages_installed", result["passed"])

    def test_non_bool_check_value_raises_type_error(self):
        for bad_value in (1, "true", None):
            with self.subTest(bad_value=bad_value):
                with self.assertRaises(TypeError):
                    check_vm_readiness(make_vm(os_supported=bad_value))

    def test_non_dict_input_raises_type_error(self):
        for bad_input in (None, [], "web-app-01"):
            with self.subTest(bad_input=bad_input):
                with self.assertRaises(TypeError):
                    check_vm_readiness(bad_input)

    def test_missing_or_blank_vm_name_raises_value_error(self):
        cases = [
            make_vm(vm_name=""),
            make_vm(vm_name="   "),
            {"os_supported": True},  # missing vm_name
        ]
        for vm in cases:
            with self.subTest(vm=vm):
                with self.assertRaises(ValueError):
                    check_vm_readiness(vm)

    def test_non_string_vm_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            check_vm_readiness(make_vm(vm_name=123))

    def test_does_not_mutate_input(self):
        vm = make_vm(network_configured=False)
        original = copy.deepcopy(vm)

        check_vm_readiness(vm)

        self.assertEqual(vm, original)


if __name__ == "__main__":
    unittest.main()
