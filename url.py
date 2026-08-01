#!/usr/bin/env python3
"""url — URL shortener and validator for the command line.

Validate URL format, expand shortened URLs, and extract components
(scheme, host, path, params, query, fragment). Zero external dependencies.

Usage:
    url validate <url>       Validate URL format
    url expand <url>         Expand shortened URL (follow redirects)
    url parse <url>          Extract URL components
    url --help               Show this help
    url --version            Show version
"""

import argparse
import re
import sys
import urllib.parse
import urllib.request
from typing import Optional

__version__ = "0.1.0"

# Regex for basic URL sanity (scheme://host)
_URL_RE = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9+.-]*://"
    r"[^\s/$.?#]"
    r"[^\s]*$",
    re.IGNORECASE,
)


def validate(url: str) -> bool:
    """Return True if *url* is a syntactically valid absolute URL."""
    if not url or not url.strip():
        return False
    url = url.strip()
    if not _URL_RE.match(url):
        return False
    try:
        result = urllib.parse.urlparse(url)
    except ValueError:
        return False
    if not result.scheme or not result.netloc:
        return False
    if result.scheme not in ("http", "https"):
        return False
    return True


def expand(url: str, timeout: int = 10) -> str:
    """Follow redirects and return the final resolved URL.

    Raises ValueError on network errors or non-HTTP schemes.
    """
    if not validate(url):
        raise ValueError(f"Invalid URL: {url}")

    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.url
    except urllib.error.HTTPError:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.url
        except urllib.error.HTTPError as exc2:
            raise ValueError(f"HTTP error {exc2.code} for {url}") from exc2
        except urllib.error.URLError as exc2:
            raise ValueError(f"Network error resolving {url}: {exc2.reason}") from exc2
    except urllib.error.URLError as exc:
        raise ValueError(f"Network error resolving {url}: {exc.reason}") from exc


def parse(url: str) -> dict:
    """Extract components from a URL.

    Returns a dict with keys: scheme, netloc, hostname, port, path,
    params, query, fragment, query_params (dict).
    """
    parsed = urllib.parse.urlparse(url)
    result = {
        "scheme": parsed.scheme or None,
        "netloc": parsed.netloc or None,
        "hostname": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path or None,
        "params": parsed.params or None,
        "query": parsed.query or None,
        "fragment": parsed.fragment or None,
        "query_params": {},
    }
    if parsed.query:
        qp = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        result["query_params"] = {k: v[0] if len(v) == 1 else v for k, v in qp.items()}
    return result


def cmd_validate(args: argparse.Namespace) -> int:
    """Run the 'validate' subcommand."""
    if validate(args.url):
        print(f"valid: {args.url}")
        return 0
    else:
        print(f"invalid: {args.url}", file=sys.stderr)
        print("  URLs must have a scheme (http/https) and a host.", file=sys.stderr)
        return 1


def cmd_expand(args: argparse.Namespace) -> int:
    """Run the 'expand' subcommand."""
    if not validate(args.url):
        print(f"invalid: {args.url}", file=sys.stderr)
        print("  URLs must have a scheme (http/https) and a host.", file=sys.stderr)
        return 1
    try:
        resolved = expand(args.url, timeout=args.timeout)
        if resolved == args.url:
            print(f"no redirect: {args.url}")
        else:
            print(f"redirect: {args.url} -> {resolved}")
        return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def cmd_parse(args: argparse.Namespace) -> int:
    """Run the 'parse' subcommand."""
    if not args.url.strip():
        print("error: No URL provided", file=sys.stderr)
        return 1

    components = parse(args.url)
    print(f"URL: {args.url}")
    print(f"  scheme:    {components['scheme'] or '(none)'}")
    print(f"  netloc:    {components['netloc'] or '(none)'}")
    print(f"  hostname:  {components['hostname'] or '(none)'}")
    print(f"  port:      {components['port'] or '(default)'}")
    print(f"  path:      {components['path'] or '/'}")
    print(f"  params:    {components['params'] or '(none)'}")
    print(f"  query:     {components['query'] or '(none)'}")
    print(f"  fragment:  {components['fragment'] or '(none)'}")
    if components["query_params"]:
        print("  query_params:")
        for k, v in components["query_params"].items():
            print(f"    {k} = {v}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="url",
        description="URL shortener and validator for the command line.",
        epilog="Examples:\n"
        "  url validate https://example.com\n"
        "  url expand https://bit.ly/3ABCxyz\n"
        "  url parse https://example.com/path?a=1&b=2#section\n"
        "  url --version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate URL format")
    p_validate.add_argument("url", help="URL to validate")

    p_expand = sub.add_parser("expand", help="Expand shortened URL (follow redirects)")
    p_expand.add_argument("url", help="URL to expand")
    p_expand.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout in seconds (default: 10)",
    )

    p_parse = sub.add_parser("parse", help="Extract URL components")
    p_parse.add_argument("url", help="URL to parse")

    return parser


def main(argv: Optional[list] = None) -> int:
    """Entry point. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "validate": cmd_validate,
        "expand": cmd_expand,
        "parse": cmd_parse,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
