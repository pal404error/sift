# Contributing to Sift

Hey there! 👋 First off, thank you for considering contributing to Sift. It's people like you that make open-source software such a fantastic community.

Whether you're fixing a typo, adding a new model provider, or building out a massive new feature, we are thrilled to have your help.

## Getting Started

Let's get your local environment set up. It's quick and painless!

### 1. Fork & Clone
Fork the repository on GitHub, then clone it locally:
```bash
git clone https://github.com/YOUR_USERNAME/sift.git
cd sift
```

### 2. Set Up Your Virtual Environment
We strongly recommend using a virtual environment to keep dependencies clean. Sift requires Python 3.10+.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install for Development
Install the project in editable mode along with the development dependencies:

```bash
pip install -e ".[dev]"
```

## Making Changes

We use a few standard quality gates to keep the codebase healthy and clean.

- **Formatting & Linting**: We use `ruff`. Run it before committing:
  ```bash
  ruff check .
  ruff format .
  ```
- **Type Checking**: We love static types. Make sure `mypy` is happy:
  ```bash
  mypy sift/
  ```
- **Testing**: We use `pytest`. Ensure all tests pass:
  ```bash
  pytest
  ```

## Branch & Pull Request Flow

1. **Branch out**: Create a new branch for your feature or bugfix (e.g., `git checkout -b feature/awesome-new-provider`).
2. **Commit clearly**: Write descriptive commit messages.
3. **Push up**: Push your branch to your fork.
4. **Open a PR**: Open a Pull Request against the `main` branch of the `pal404error/sift` repository. 

Don't worry if your PR isn't perfect on the first try. We're here to review, help, and iterate with you!

## Where Things Live

- `sift/` - The core application code (FastAPI, orchestration, providers).
- `cli/` - The `sift` CLI tool.
- `web/` - The static web UI.
- `tests/` - Unit and integration tests.
- `docs/` - Project documentation. If you're updating docs, this is the place to be!

Thanks again for being part of the Sift journey! 🚀
