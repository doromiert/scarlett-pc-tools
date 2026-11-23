"""Tests use generated PE structure only, never bytes from a commercial binary."""
import json
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest
import subprocess
from unittest.mock import patch

import scarlett_pc_tools as tools


def synthetic_pe():
    data = bytearray(0x800)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 0x84, 0x8664, 2, 0, 0, 0, 240, 0x22)
    opt = 0x98
    struct.pack_into("<H", data, opt, 0x20B)
    struct.pack_into("<I", data, opt + 16, 0x1000)
    struct.pack_into("<Q", data, opt + 24, 0x140000000)
    struct.pack_into("<II", data, opt + 32, 0x1000, 0x200)
    struct.pack_into("<II", data, opt + 56, 0x3000, 0x200)
    struct.pack_into("<H", data, opt + 68, 3)
    struct.pack_into("<I", data, opt + 108, 16)
    struct.pack_into("<II", data, opt + 120, 0x2000, 40)
    section = opt + 240
    for i, (name, va, raw, size, flags) in enumerate([
            (b".text", 0x1000, 0x200, 0x200, 0x60000020),
            (b".rdata", 0x2000, 0x400, 0x400, 0x40000040)]):
        at = section + i * 40
        data[at:at+len(name)] = name
        struct.pack_into("<IIII", data, at + 8, size, va, size, raw)
        struct.pack_into("<I", data, at + 36, flags)
    data[0x200] = 0xC3
    struct.pack_into("<IIIII", data, 0x400, 0x20C0, 0, 0, 0x2080, 0x20E0)
    data[0x480:0x48D] = b"d3d12_xs.dll\0"
    struct.pack_into("<Q", data, 0x4C0, 0x2100)
    struct.pack_into("<Q", data, 0x4E0, 0x2100)
    name = b"D3D12XboxCreateDevice\0"
    data[0x502:0x502+len(name)] = name
    return bytes(data)


class ToolsTests(unittest.TestCase):
    def test_inspect_synthetic_import_and_missing_chunk(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.exe").write_bytes(synthetic_pe())
            (root / "MicrosoftGame.Config").write_text(
                '<Game><ExecutableList><Executable Name="sample.exe" TargetDeviceFamily="Scarlett"/>'
                '</ExecutableList></Game>')
            (root / "layout_test.xml").write_text(
                '<Package><Chunk Id="1"><FileGroup DestinationPath="\\" Include="sample.exe"/>'
                '<FileGroup DestinationPath="\\" Include="missing.rpf"/></Chunk></Package>')
            report = tools.inspect(root)
            self.assertEqual(report["machine"], "0x8664")
            self.assertEqual(report["imports"][0]["functions"], ["D3D12XboxCreateDevice"])
            self.assertTrue(report["imports"][0]["requires_console_runtime"])
            self.assertFalse(report["layouts"][0]["chunks"][0]["files"][1]["present"])

    def test_rejects_destination_traversal_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "dump"
            root.mkdir()
            with self.assertRaises(ValueError):
                tools.destination(root, "", "../private.exe")
            (root / "escape").symlink_to(root.parent, target_is_directory=True)
            with self.assertRaises(ValueError):
                tools.destination(root, "escape", "private.exe")

    def test_git_reports_refused_before_file_access(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            with patch.object(tools, "inspect") as inspect:
                self.assertEqual(tools.main(["inspect", "nonexistent", "--output", str(root / "report.json")]), 1)
                inspect.assert_not_called()

    def test_timeout_stops_worker_and_cannot_reuse_previous_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "boot.json").write_text('{"phase":"old-success"}')
            started = time.monotonic()
            result = tools.run_worker([sys.executable, "-c", "import time; time.sleep(30)"], root, 0.1)
            self.assertEqual(result["status"], "timeout")
            self.assertNotIn("diagnostic", result)
            self.assertLess(time.monotonic() - started, 3)
            self.assertEqual(len(list(root.glob("attempt-*/summary.json"))), 1)

    def test_invalid_pe_returns_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.exe"
            path.write_text("not an executable")
            self.assertEqual(tools.main(["inspect", str(path)]), 1)

    def test_public_tree_guard_checks_staged_bytes(self):
        script = Path(tools.__file__).parent / "scripts/check_public_tree.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            path = root / "payload.py"
            path.write_bytes(b"binary\0data")
            subprocess.run(["git", "-C", str(root), "add", "payload.py"], check=True)
            path.write_text("# working tree looks innocent\n")
            r = subprocess.run([sys.executable, str(script)], cwd=root, capture_output=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn(b"Binary or oversized", r.stderr)

    def test_public_tree_guard_rejects_force_added_game_extension(self):
        script = Path(tools.__file__).parent / "scripts/check_public_tree.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "sample.rpf").write_text("synthetic fixture")
            subprocess.run(["git", "-C", str(root), "add", "sample.rpf"], check=True)
            r = subprocess.run([sys.executable, str(script)], cwd=root, capture_output=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn(b"Unapproved tracked file type", r.stderr)


if __name__ == "__main__":
    unittest.main()
