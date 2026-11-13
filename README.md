# Markdown Map

Index a Markdown documentation tree and audit local links.

## Features

- Recursive heading and document inventory
- Local Markdown/file-link checks and missing-target reports
- Case-insensitive document search
- Fenced-code exclusion and symlink-safe workspace boundaries

## Get started

Requires **Python 3.11+**. No third-party packages or installation step.

```sh
git clone https://github.com/oexwashere/markdown-map.git
cd markdown-map
python3 app.py --help
```

## Examples

```sh
python3 app.py examples/docs --check
python3 app.py examples/docs --search installation
python3 app.py /path/to/documentation --check
```

Example files are intentionally small and contain no real credentials or user data. Output goes to stdout, making it easy to redirect into a report. Errors go to stderr.

## Verify

```sh
python3 -m unittest -v
python3 -m py_compile app.py
```

Tests use temporary directories when filesystem access is needed. They do not modify your working data or require a network connection. GitHub Actions is configured for Python 3.11, 3.12, and 3.13.

## Architecture

`app.py` contains the reusable functions and CLI entry point. `test_app.py` exercises boundary conditions and representative workflows. `examples/` contains runnable fixtures.

An explicit fence state excludes fenced code examples. The scanner inventories ATX headings and inline file links, resolves percent-encoded paths, and checks that local targets stay within the workspace. External URLs are recorded but never requested.

## Exit codes

`0` means the requested operation completed; `2` means a usage, input, or filesystem failure. `1` means unreadable documents or, with `--check`, broken local links were found.

## Limitations and data handling

This is a deliberately small Markdown subset. It does not validate fragments/heading anchors, reference-style links, embedded HTML links, or all nested-parenthesis constructs. Search filters returned documents; broken-link auditing still covers the full tree. Root-relative links are interpreted relative to the selected directory.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep changes focused and include a regression test when behavior changes.

## License

[MIT](LICENSE) · oexwashere
