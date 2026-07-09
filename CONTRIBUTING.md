# Contributing to SOTA Research Workflow

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Guidelines

- Follow PEP 8 style guide for Python code
- Add docstrings for all new functions
- Test with both Chinese and English queries
- Ensure no hardcoded API keys/tokens in source code
- Update SKILL.md version number for any API changes

## Adding New CodeSOTA Task Mappings

Edit `config/codesota_tasks.json` to add:
- New Chinese-to-English task mappings
- New keyword associations
- New task IDs

## Reporting Issues

Please include:
- Your query (Chinese or English)
- Expected vs actual behavior
- API error messages (if any)
- Python version and OS
