# url

URL shortener and validator for the command line. Validate URL format, expand shortened URLs by following redirects, and extract components (scheme, host, path, params, query, fragment). Zero external dependencies — uses only Python stdlib (`urllib.parse`, `argparse`, `re`).

```bash
# Install (copy to your PATH)
cp url.py /usr/local/bin/url
chmod +x /usr/local/bin/url

# Validate a URL
url validate https://example.com

# Expand a shortened URL
url expand https://bit.ly/3ABCxyz

# Parse URL components
url parse "https://example.com/path?name=ferret&color=purple#section"
```
