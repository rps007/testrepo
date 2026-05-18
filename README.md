# testrepo

Simple Python CLI to scrape a website, run a regex search, and save the last 10 patterns used.

## Usage

```bash
python scrape_search.py --url "https://example.com" --pattern "Example"
```

If `--pattern` is omitted, the CLI prompts you to enter one.

```bash
python scrape_search.py --url "https://example.com"
```

Show saved patterns:

```bash
python scrape_search.py --url "https://example.com" --show-history
```

## Notes

- Pattern history is saved in `.regex_pattern_history.json` (last 10 patterns).
- Add `--ignore-case` for case-insensitive matching.
