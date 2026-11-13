# Design notes

## Scope

Index a Markdown documentation tree and audit local links.

## Implementation decisions

An explicit fence state excludes fenced code examples. The scanner inventories ATX headings and inline file links, resolves percent-encoded paths, and checks that local targets stay within the workspace. External URLs are recorded but never requested.

## Boundaries

This is a deliberately small Markdown subset. It does not validate fragments/heading anchors, reference-style links, embedded HTML links, or all nested-parenthesis constructs. Search filters returned documents; broken-link auditing still covers the full tree. Root-relative links are interpreted relative to the selected directory.

## Verification

The Python unittest suite uses deterministic fixtures and temporary directories for filesystem tests.

Tests describe expected behavior rather than depending on a live external service. CI configuration is included, but remote CI execution is not implied by local test results.
