# Screenshot & Evidence Capture Engine

A professional evidence capture tool using Selenium WebDriver. Capable of taking full-page screenshots, mobile view screenshots, capturing specific elements, logging network traffic, and saving HTTP responses.

## Features

- **Full Page Screenshots**: Captures the entire scrollable area of a page.
- **Mobile Emulation**: Captures screenshots as seen on a mobile device (iPhone emulation).
- **Element Selector**: Captures screenshots of specific DOM elements via CSS selectors.
- **Network Logging**: Captures and saves network performance logs (HAR-like data).
- **HTTP Response Capture**: Saves raw HTTP headers and response bodies.
- **Evidence Reporting**: Generates a JSON report linking all captured artifacts.

## Dependencies

- `selenium`
- `pillow`
- `requests`
- `chrome` and `chromedriver` (must be in PATH)

## Usage

```bash
# Capture full page
python screenshot_engine.py https://example.com --fullpage

# Capture everything (fullpage, mobile, network, http)
python screenshot_engine.py https://example.com --all

# Capture specific element
python screenshot_engine.py https://example.com --element "#main-content"
```

## Output

All evidence is saved to the `evidence/` directory by default.
