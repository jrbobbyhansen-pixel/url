"""Tests for url CLI tool."""

import sys
import subprocess
import pytest

# Import the module directly for unit tests
sys.path.insert(0, "/tmp/url-rebuild")
import url as urlmod


# ── validate() unit tests ──────────────────────────────────────────────

class TestValidate:
    def test_valid_https(self):
        assert urlmod.validate("https://example.com") is True

    def test_valid_http(self):
        assert urlmod.validate("http://example.com") is True

    def test_valid_with_path(self):
        assert urlmod.validate("https://example.com/path/to/page") is True

    def test_valid_with_query(self):
        assert urlmod.validate("https://example.com/search?q=hello&lang=en") is True

    def test_valid_with_fragment(self):
        assert urlmod.validate("https://example.com/page#section") is True

    def test_valid_with_port(self):
        assert urlmod.validate("https://example.com:8080/path") is True

    def test_valid_subdomain(self):
        assert urlmod.validate("https://sub.example.com") is True

    def test_valid_ip(self):
        assert urlmod.validate("https://192.168.1.1") is True

    def test_invalid_no_scheme(self):
        assert urlmod.validate("example.com") is False

    def test_invalid_empty_string(self):
        assert urlmod.validate("") is False

    def test_invalid_whitespace(self):
        assert urlmod.validate("   ") is False

    def test_invalid_ftp_scheme(self):
        assert urlmod.validate("ftp://example.com") is False

    def test_invalid_mailto(self):
        assert urlmod.validate("mailto:user@example.com") is False

    def test_invalid_javascript(self):
        assert urlmod.validate("javascript:void(0)") is False

    def test_invalid_spaces_in_url(self):
        assert urlmod.validate("https://exa mple.com") is False

    def test_invalid_no_host(self):
        assert urlmod.validate("https://") is False

    def test_invalid_scheme_only(self):
        assert urlmod.validate("https:///path") is False


# ── parse() unit tests ────────────────────────────────────────────────

class TestParse:
    def test_basic_parse(self):
        result = urlmod.parse("https://example.com/path")
        assert result["scheme"] == "https"
        assert result["hostname"] == "example.com"
        assert result["path"] == "/path"

    def test_parse_with_query(self):
        result = urlmod.parse("https://example.com/search?q=hello&lang=en")
        assert result["query"] == "q=hello&lang=en"
        assert result["query_params"] == {"q": "hello", "lang": "en"}

    def test_parse_with_fragment(self):
        result = urlmod.parse("https://example.com/page#section")
        assert result["fragment"] == "section"

    def test_parse_with_port(self):
        result = urlmod.parse("https://example.com:8080/path")
        assert result["port"] == 8080

    def test_parse_no_path(self):
        result = urlmod.parse("https://example.com")
        assert result["path"] is None

    def test_parse_no_query(self):
        result = urlmod.parse("https://example.com")
        assert result["query"] is None
        assert result["query_params"] == {}

    def test_parse_no_fragment(self):
        result = urlmod.parse("https://example.com")
        assert result["fragment"] is None

    def test_parse_duplicate_query_params(self):
        result = urlmod.parse("https://example.com?a=1&a=2")
        assert isinstance(result["query_params"]["a"], list)
        assert result["query_params"]["a"] == ["1", "2"]


# ── CLI integration tests ─────────────────────────────────────────────

class TestCLI:
    def run(self, *args):
        result = subprocess.run(
            [sys.executable, "/tmp/url-rebuild/url.py"] + list(args),
            capture_output=True,
            text=True,
        )
        return result

    def test_validate_valid(self):
        r = self.run("validate", "https://example.com")
        assert r.returncode == 0
        assert "valid:" in r.stdout

    def test_validate_invalid(self):
        r = self.run("validate", "not-a-url")
        assert r.returncode == 1
        assert "invalid:" in r.stderr

    def test_parse_basic(self):
        r = self.run("parse", "https://example.com/path")
        assert r.returncode == 0
        assert "scheme:" in r.stdout
        assert "https" in r.stdout
        assert "hostname:" in r.stdout
        assert "example.com" in r.stdout

    def test_parse_empty(self):
        r = self.run("parse", "")
        assert r.returncode == 1
        assert "error:" in r.stderr

    def test_version(self):
        r = self.run("--version")
        assert r.returncode == 0
        assert "0.1.0" in r.stdout

    def test_help(self):
        r = self.run("--help")
        assert r.returncode == 0
        assert "validate" in r.stdout
        assert "expand" in r.stdout
        assert "parse" in r.stdout

    def test_no_command(self):
        r = self.run()
        assert r.returncode == 2  # argparse error
