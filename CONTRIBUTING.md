# Contributing to API Explorer

## How to Contribute

We welcome contributions from the community! Here are the ways you can help:

- **Report bugs** — Open an issue describing the problem and steps to reproduce it.
- **Suggest features** — Open an issue with a detailed description of the proposed feature.
- **Submit code** — Fork the repository, make your changes, and open a pull request.
- **Improve documentation** — Fix typos, clarify instructions, or add missing information.

## Development Setup

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```
   git clone https://github.com/puretechteam/api-explorer.git
   ```
3. Navigate to the project directory:
   ```
   cd api-explorer
   ```
4. Create a virtual environment:
   ```
   python -m venv venv
   ```
5. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```
6. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```
7. Run the development server:
   ```
   python app.py
   ```

## Submitting Changes

1. Create a new branch for your feature or bug fix:
   ```
   git checkout -b my-feature
   ```
2. Make your changes and commit them with a clear, descriptive commit message.
3. Push your branch to your fork:
   ```
   git push origin my-feature
   ```
4. Open a pull request against the `main` branch of the `puretechteam/api-explorer` repository.
5. Ensure all checks pass and your PR description clearly explains the changes.

## Code Style Guidelines

- Follow PEP 8 for Python code.
- Use 4-space indentation (no tabs).
- Use descriptive variable and function names.
- Keep lines under 88 characters (Black default).
- Format code with `black` before submitting.
- Lint with `flake8` or `ruff` to catch issues early.
- Write docstrings for all public functions and classes.
- Keep changes focused — one logical change per pull request.