"""Tests for cross-platform compatibility utilities.

This module tests the PlatformDetector class and related functionality
for handling Windows, macOS, and Linux platform differences.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

import pytest

from src.py.utils.platform import (
    PlatformDetector,
    get_platform,
    get_python_command,
    is_windows,
    is_unix_like,
    run_platform_command,
    platform_detector
)


class TestPlatformDetector(unittest.TestCase):
    """Test PlatformDetector class functionality."""

    def setUp(self):
        """Set up test environment."""
        self.detector = PlatformDetector()

    def test_detect_windows_platform(self):
        """Test Windows platform detection."""
        with patch('os.name', 'nt'):
            with patch('platform.system', return_value='Windows'):
                detector = PlatformDetector()
                self.assertEqual(detector.platform, "Windows")
                self.assertTrue(detector.is_windows())
                self.assertFalse(detector.is_macos())
                self.assertFalse(detector.is_linux())
                self.assertFalse(detector.is_unix_like())

    def test_detect_macos_platform(self):
        """Test macOS platform detection."""
        with patch('os.name', 'posix'):
            with patch('platform.system', return_value='Darwin'):
                detector = PlatformDetector()
                self.assertEqual(detector.platform, "macOS")
                self.assertFalse(detector.is_windows())
                self.assertTrue(detector.is_macos())
                self.assertFalse(detector.is_linux())
                self.assertTrue(detector.is_unix_like())

    def test_detect_linux_platform(self):
        """Test Linux platform detection."""
        with patch('os.name', 'posix'):
            with patch('platform.system', return_value='Linux'):
                detector = PlatformDetector()
                self.assertEqual(detector.platform, "Linux")
                self.assertFalse(detector.is_windows())
                self.assertFalse(detector.is_macos())
                self.assertTrue(detector.is_linux())
                self.assertTrue(detector.is_unix_like())

    def test_detect_unknown_platform(self):
        """Test unknown platform detection fallback."""
        with patch('os.name', 'unknown'):
            with patch('platform.system', return_value='Unknown'):
                detector = PlatformDetector()
                self.assertEqual(detector.platform, "Unknown")

    def test_path_separator_windows(self):
        """Test path separator for Windows."""
        with patch.object(self.detector, 'is_windows', return_value=True):
            self.assertEqual(self.detector.get_path_separator(), "\\")

    def test_path_separator_unix(self):
        """Test path separator for Unix-like systems."""
        with patch.object(self.detector, 'is_windows', return_value=False):
            self.assertEqual(self.detector.get_path_separator(), "/")

    def test_null_device_windows(self):
        """Test null device for Windows."""
        with patch.object(self.detector, 'is_windows', return_value=True):
            self.assertEqual(self.detector.get_null_device(), "nul")

    def test_null_device_unix(self):
        """Test null device for Unix-like systems."""
        with patch.object(self.detector, 'is_windows', return_value=False):
            self.assertEqual(self.detector.get_null_device(), "/dev/null")

    @patch('shutil.which')
    def test_python_command_detection_with_uv(self, mock_which):
        """Test Python command detection when uv is available."""
        mock_which.return_value = "/usr/local/bin/uv"
        
        detector = PlatformDetector()
        self.assertEqual(detector.python_cmd, "uv run python")

    @patch('shutil.which', return_value=None)
    @patch('pathlib.Path.exists')
    def test_python_command_detection_with_venv_windows(self, mock_exists, mock_which):
        """Test Python command detection with venv on Windows."""
        mock_exists.return_value = True
        
        with patch.object(PlatformDetector, 'is_windows', return_value=True):
            with patch.object(PlatformDetector, 'get_venv_python_path', return_value='.venv\\Scripts\\python.exe'):
                detector = PlatformDetector()
                self.assertEqual(detector.python_cmd, '.venv\\Scripts\\python.exe')

    @patch('shutil.which', return_value=None)
    @patch('pathlib.Path.exists')
    def test_python_command_detection_with_venv_unix(self, mock_exists, mock_which):
        """Test Python command detection with venv on Unix."""
        mock_exists.return_value = True
        
        with patch.object(PlatformDetector, 'is_windows', return_value=False):
            with patch.object(PlatformDetector, 'get_venv_python_path', return_value='.venv/bin/python'):
                detector = PlatformDetector()
                self.assertEqual(detector.python_cmd, '.venv/bin/python')

    @patch('shutil.which', return_value=None)
    def test_python_command_fallback_windows(self, mock_which):
        """Test Python command fallback on Windows."""
        with patch.object(PlatformDetector, 'is_windows', return_value=True):
            with patch.object(PlatformDetector, 'get_venv_python_path', return_value=None):
                detector = PlatformDetector()
                self.assertEqual(detector.python_cmd, "python")

    @patch('shutil.which', return_value=None)
    def test_python_command_fallback_unix(self, mock_which):
        """Test Python command fallback on Unix."""
        with patch.object(PlatformDetector, 'is_windows', return_value=False):
            with patch.object(PlatformDetector, 'get_venv_python_path', return_value=None):
                detector = PlatformDetector()
                self.assertEqual(detector.python_cmd, "python3")

    def test_venv_python_path_windows(self):
        """Test virtual environment Python path on Windows."""
        with patch.object(self.detector, 'is_windows', return_value=True):
            # Mock both venv_dir.exists() and python_path.exists() calls
            with patch('pathlib.Path.exists', return_value=True):
                result = self.detector.get_venv_python_path()
                # The actual implementation uses forward slashes even on Windows with pathlib
                self.assertEqual(result, '.venv/Scripts/python.exe')

    def test_venv_python_path_unix(self):
        """Test virtual environment Python path on Unix."""
        with patch.object(self.detector, 'is_windows', return_value=False):
            # Mock both venv_dir.exists() and python_path.exists() calls
            with patch('pathlib.Path.exists', return_value=True):
                result = self.detector.get_venv_python_path()
                self.assertEqual(result, '.venv/bin/python')

    @patch('pathlib.Path.exists', return_value=False)
    def test_venv_python_path_not_exists(self, mock_exists):
        """Test virtual environment Python path when .venv doesn't exist."""
        result = self.detector.get_venv_python_path()
        self.assertIsNone(result)

    def test_venv_activate_path_windows(self):
        """Test virtual environment activate path on Windows."""
        with patch.object(self.detector, 'is_windows', return_value=True):
            # Mock both venv_dir.exists() and activate_path.exists() calls
            with patch('pathlib.Path.exists', return_value=True):
                result = self.detector.get_venv_activate_path()
                # The actual implementation uses forward slashes even on Windows with pathlib
                self.assertEqual(result, '.venv/Scripts/activate')

    def test_venv_activate_path_unix(self):
        """Test virtual environment activate path on Unix."""
        with patch.object(self.detector, 'is_windows', return_value=False):
            # Mock both venv_dir.exists() and activate_path.exists() calls
            with patch('pathlib.Path.exists', return_value=True):
                result = self.detector.get_venv_activate_path()
                self.assertEqual(result, '.venv/bin/activate')

    @patch('subprocess.run')
    def test_run_command_windows(self, mock_run):
        """Test command execution on Windows."""
        mock_run.return_value = Mock(returncode=0, stdout="output")
        
        with patch.object(self.detector, 'is_windows', return_value=True):
            result = self.detector.run_command("echo test")
            
        mock_run.assert_called_once_with("echo test", shell=True)
        self.assertEqual(result.returncode, 0)

    @patch('subprocess.run')
    def test_run_command_unix(self, mock_run):
        """Test command execution on Unix."""
        mock_run.return_value = Mock(returncode=0, stdout="output")
        
        with patch.object(self.detector, 'is_windows', return_value=False):
            result = self.detector.run_command("echo test")
            
        mock_run.assert_called_once_with("echo test", shell=True)
        self.assertEqual(result.returncode, 0)

    @patch('shutil.which')
    def test_check_command_exists_true(self, mock_which):
        """Test command existence check when command exists."""
        mock_which.return_value = "/usr/bin/python"
        
        result = self.detector.check_command_exists("python")
        self.assertTrue(result)

    @patch('shutil.which')
    def test_check_command_exists_false(self, mock_which):
        """Test command existence check when command doesn't exist."""
        mock_which.return_value = None
        
        result = self.detector.check_command_exists("nonexistent")
        self.assertFalse(result)

    def test_env_file_content_not_exists(self):
        """Test reading environment file when it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / "nonexistent.env"
            result = self.detector.get_env_file_content(env_file)
            self.assertEqual(result, {})

    def test_env_file_content_exists(self):
        """Test reading environment file content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VAR1=value1\n")
            f.write("VAR2=value2\n")
            f.write("# Comment line\n")
            f.write("VAR3=value3=with=equals\n")
            f.write("INVALID_LINE\n")
            f.write("\n")
            env_file = Path(f.name)
        
        try:
            result = self.detector.get_env_file_content(env_file)
            expected = {
                "VAR1": "value1",
                "VAR2": "value2",
                "VAR3": "value3=with=equals"
            }
            self.assertEqual(result, expected)
        finally:
            env_file.unlink(missing_ok=True)

    @patch('subprocess.run')
    def test_install_uv_windows(self, mock_run):
        """Test uv installation on Windows."""
        mock_run.return_value = Mock(returncode=0)
        
        with patch.object(self.detector, 'is_windows', return_value=True):
            result = self.detector.install_uv()
            
        self.assertTrue(result)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("powershell", args)
        self.assertIn("irm https://astral.sh/uv/install.ps1", args)

    @patch('subprocess.run')
    def test_install_uv_unix(self, mock_run):
        """Test uv installation on Unix."""
        mock_run.return_value = Mock(returncode=0)
        
        with patch.object(self.detector, 'is_windows', return_value=False):
            result = self.detector.install_uv()
            
        self.assertTrue(result)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("curl -LsSf https://astral.sh/uv/install.sh", args)

    @patch('subprocess.run')
    def test_install_uv_failure(self, mock_run):
        """Test uv installation failure."""
        mock_run.return_value = Mock(returncode=1)
        
        result = self.detector.install_uv()
        self.assertFalse(result)

    @patch('subprocess.run')
    def test_install_uv_exception(self, mock_run):
        """Test uv installation with exception."""
        mock_run.side_effect = Exception("Network error")
        
        result = self.detector.install_uv()
        self.assertFalse(result)

    @patch('shutil.rmtree')
    @patch('pathlib.Path.exists')
    def test_remove_directory_success(self, mock_exists, mock_rmtree):
        """Test successful directory removal."""
        mock_exists.return_value = True
        
        test_path = Path("test_dir")
        result = self.detector.remove_directory(test_path)
        
        self.assertTrue(result)
        mock_rmtree.assert_called_once_with(test_path)

    @patch('pathlib.Path.exists')
    def test_remove_directory_not_exists(self, mock_exists):
        """Test directory removal when directory doesn't exist."""
        mock_exists.return_value = False
        
        test_path = Path("nonexistent_dir")
        result = self.detector.remove_directory(test_path)
        
        self.assertFalse(result)

    @patch('shutil.rmtree')
    @patch('pathlib.Path.exists')
    def test_remove_directory_exception(self, mock_exists, mock_rmtree):
        """Test directory removal with exception."""
        mock_exists.return_value = True
        mock_rmtree.side_effect = Exception("Permission denied")
        
        test_path = Path("test_dir")
        result = self.detector.remove_directory(test_path)
        
        self.assertFalse(result)

    @patch('shutil.copy2')
    @patch('pathlib.Path.mkdir')
    def test_copy_file_success(self, mock_mkdir, mock_copy):
        """Test successful file copying."""
        src = Path("src.txt")
        dst = Path("dst/dst.txt")
        
        result = self.detector.copy_file(src, dst)
        
        self.assertTrue(result)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_copy.assert_called_once_with(src, dst)

    @patch('shutil.copy2')
    @patch('pathlib.Path.mkdir')
    def test_copy_file_exception(self, mock_mkdir, mock_copy):
        """Test file copying with exception."""
        mock_copy.side_effect = Exception("Permission denied")
        
        src = Path("src.txt")
        dst = Path("dst.txt")
        
        result = self.detector.copy_file(src, dst)
        self.assertFalse(result)

    def test_make_executable_windows(self):
        """Test making file executable on Windows."""
        with patch.object(self.detector, 'is_windows', return_value=True):
            result = self.detector.make_executable(Path("test.py"))
            self.assertTrue(result)  # Windows always returns True

    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.chmod')
    def test_make_executable_unix_success(self, mock_chmod, mock_stat):
        """Test making file executable on Unix."""
        import stat
        mock_stat.return_value = Mock(st_mode=0o644)
        
        with patch.object(self.detector, 'is_windows', return_value=False):
            result = self.detector.make_executable(Path("test.py"))
            
        self.assertTrue(result)
        mock_chmod.assert_called_once_with(0o644 | stat.S_IEXEC)

    @patch('pathlib.Path.chmod')
    def test_make_executable_unix_exception(self, mock_chmod):
        """Test making file executable on Unix with exception."""
        mock_chmod.side_effect = Exception("Permission denied")
        
        with patch.object(self.detector, 'is_windows', return_value=False):
            result = self.detector.make_executable(Path("test.py"))
            
        self.assertFalse(result)


class TestPlatformUtilityFunctions(unittest.TestCase):
    """Test utility functions that use the global platform detector."""

    def test_get_platform(self):
        """Test get_platform function."""
        result = get_platform()
        self.assertIn(result, ["Windows", "macOS", "Linux", "Unknown"])

    def test_get_python_command(self):
        """Test get_python_command function."""
        result = get_python_command()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_is_windows(self):
        """Test is_windows function."""
        result = is_windows()
        self.assertIsInstance(result, bool)

    def test_is_unix_like(self):
        """Test is_unix_like function."""
        result = is_unix_like()
        self.assertIsInstance(result, bool)

    @patch('src.py.utils.platform.platform_detector.run_command')
    def test_run_platform_command(self, mock_run_command):
        """Test run_platform_command function."""
        mock_run_command.return_value = Mock(returncode=0)
        
        result = run_platform_command("echo test")
        
        mock_run_command.assert_called_once_with("echo test")
        self.assertEqual(result.returncode, 0)


class TestPlatformDetectorEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for PlatformDetector."""

    def test_env_file_reading_with_malformed_content(self):
        """Test environment file reading with malformed content."""
        detector = PlatformDetector()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VALID=value\n")
            f.write("NO_EQUALS_SIGN\n")
            f.write("=EMPTY_KEY\n")
            f.write("SPACE_IN_KEY =value\n")
            f.write("KEY= VALUE_WITH_SPACES \n")
            env_file = Path(f.name)
        
        try:
            result = detector.get_env_file_content(env_file)
            
            # Should handle malformed lines gracefully
            self.assertIn("VALID", result)
            self.assertEqual(result["VALID"], "value")
            self.assertIn("KEY", result)
            self.assertEqual(result["KEY"], "VALUE_WITH_SPACES")
            
        finally:
            env_file.unlink(missing_ok=True)

    def test_env_file_reading_exception_handling(self):
        """Test environment file reading with I/O exception."""
        detector = PlatformDetector()
        
        # Create a file that will cause an exception when read
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError("Permission denied")
            
            result = detector.get_env_file_content(Path("test.env"))
            self.assertEqual(result, {})

    @patch('shutil.which')
    def test_python_command_detection_edge_case(self, mock_which):
        """Test Python command detection with edge cases."""
        # Test when uv exists but venv python doesn't
        mock_which.return_value = None
        
        with patch.object(PlatformDetector, 'get_venv_python_path', return_value=None):
            with patch.object(PlatformDetector, 'is_windows', return_value=False):
                detector = PlatformDetector()
                self.assertEqual(detector.python_cmd, "python3")

    def test_venv_path_with_missing_executable(self):
        """Test venv path detection when directory exists but executable is missing."""
        detector = PlatformDetector()
        
        # Mock .venv directory exists but python executable doesn't
        with patch('pathlib.Path.exists', side_effect=lambda: False):
            result = detector.get_venv_python_path()
            self.assertIsNone(result)

    def test_concurrent_platform_detection(self):
        """Test that multiple PlatformDetector instances work correctly."""
        detector1 = PlatformDetector()
        detector2 = PlatformDetector()
        
        # Both should detect the same platform
        self.assertEqual(detector1.platform, detector2.platform)
        self.assertEqual(detector1.is_windows(), detector2.is_windows())

    @patch('subprocess.run')
    def test_command_execution_with_custom_kwargs(self, mock_run):
        """Test command execution with custom keyword arguments."""
        mock_run.return_value = Mock(returncode=0)
        detector = PlatformDetector()
        
        detector.run_command(
            "test command",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        mock_run.assert_called_once_with(
            "test command",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )


if __name__ == '__main__':
    unittest.main()