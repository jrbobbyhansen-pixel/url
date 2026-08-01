# url — URL Validator, Expander, and Parser

Validate URL format, expand shortened URLs by following redirects, and extract components (scheme, host, path, params, query, fragment). Zero external dependencies — uses only Python stdlib (`urllib.parse`, `argparse`, `re`). Portable across macOS, Linux, and WSL.

## Install

```bash
pip install git+https://github.com/jrbobbyhansen-pixel/url.git
```

Or just copy `url.py` anywhere on your `PATH`:

```bash
curl -O https://raw.githubusercontent.com/jrbobbyhansen-pixel/url/main/url.py
chmod +x url.py
```

## Usage

```bash
# Validate a URL
url validate https://example.com

# Expand a shortened URL
url expand https://bit.ly/3ABCxyz

# Parse URL components
url parse "https://example.com/path?name=ferret&color=purple#section"
```

Exit code: `0` on success, `1` on error.

## Test

```bash
pip install pytest
pytest -v
```

## License

MIT — see [LICENSE](LICENSE).

---

Part of the [Manta](https://github.com/jrbobbyhansen-pixel) collection — zero-dependency CLI tools for developers.
