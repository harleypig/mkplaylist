# Contributing Guide

Thank you for your interest in contributing to mkplaylist! This document
provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Git Workflow](#git-workflow)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Development Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/harleypig/mkplaylist.git
   cd mkplaylist
   ```

   ```

2. Create a virtual environment:
   ```bash
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

5. Create a `.env` file with your API credentials:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   LASTFM_API_KEY=your_lastfm_api_key
   LASTFM_API_SECRET=your_lastfm_shared_secret
   ```

## Project Structure

```
mkplaylist/
├── mkplaylist/            # Main package code
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration and API credentials
│   ├── cli.py             # Command-line interface
│   ├── database/          # Database models and operations
│   │   ├── __init__.py
│   │   ├── models.py      # SQLAlchemy models
│   │   └── db_manager.py  # Database operations
│   ├── api/               # API clients
│   │   ├── __init__.py
│   │   ├── spotify_client.py  # Spotify API client
│   │   └── lastfm_client.py   # Last.fm API client
│   └── services/          # Business logic
│       ├── __init__.py
│       ├── sync_service.py     # Data synchronization
│       ├── playlist_service.py # Playlist generation
│       └── query_parser.py     # Criteria parsing
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
│   ├── user/              # User documentation
│   └── dev/               # Developer documentation
├── setup.py               # Package setup
├── requirements.txt       # Dependencies
└── .env.example           # Example environment variables
```

## Coding Standards

### Style Guide

This project follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) style
guide for Python code.

### Code Formatting

We use the following tools to ensure code quality:

- **Black**: For code formatting
- **isort**: For import sorting
- **flake8**: For linting

You can run these tools manually:

```bash
# Format code
black mkplaylist tests

# Sort imports
isort mkplaylist tests

# Lint code
flake8 mkplaylist tests
```

These checks will also run automatically when you commit code if you've
installed the pre-commit hooks.

### Type Hints

We use type hints throughout the codebase. New code should include appropriate
type annotations:

```python
def get_track_by_id(track_id: str) -> Optional[Track]:
    """
    Get a track by its ID.

    Args:
        track_id: The Spotify ID of the track

    Returns:
        The track object if found, None otherwise
    """
    # Implementation
```

## Testing

### Running Tests

We use pytest for testing. To run the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=mkplaylist

# Run specific test file
pytest tests/unit/test_query_parser.py

# Run specific test
pytest tests/unit/test_query_parser.py::test_parse_recently_added
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Use descriptive test names that explain what is being tested

Example test:

```python
def test_parse_recently_added():
    """Test parsing 'recently added' criteria."""
    parser = QueryParser()
    criteria = "10 most recently added songs"
    query = parser.parse(criteria)

    assert query.limit == 10
    assert query.sort_by == "added_at"
    assert query.sort_order == "desc"
```

### Mocking External APIs

For tests that would normally call external APIs, use the `pytest-mock` fixture or the `unittest.mock` module to mock the API responses.

For integration tests that need to simulate API interactions, we use `vcrpy` to record and replay API responses:

```python
import vcr

@vcr.use_cassette('tests/fixtures/vcr_cassettes/spotify_get_playlist.yaml')
def test_get_playlist():
    """Test getting a playlist from Spotify."""
    client = SpotifyClient(client_id, client_secret, redirect_uri)
    client.authenticate()

    playlist = client.get_playlist('spotify:playlist:37i9dQZEVXcJZyENOWUFo7')

    assert playlist['name'] == 'Today\'s Top Hits'
    assert len(playlist['tracks']['items']) > 0
```

## Documentation

### Code Documentation

- Use docstrings for all public modules, classes, and functions
- Follow the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings
- Include type information in docstrings

Example:

```python
def create_playlist(name: str, description: str = "", public: bool = False) -> Dict[str, Any]:
    """
    Create a new Spotify playlist.

    Args:
        name: The name of the playlist
        description: Optional description for the playlist
        public: Whether the playlist should be public

    Returns:
        The created playlist data

    Raises:
        SpotifyAuthError: If authentication fails
        SpotifyAPIError: If the API request fails
    """
    # Implementation
```

### Project Documentation

- User documentation goes in `docs/user/`
- Developer documentation goes in `docs/dev/`
- Use Markdown for documentation files
- Keep documentation up to date with code changes

## Git Workflow

### Branching Strategy

- `main`: The main branch contains the latest stable release
- `develop`: Development branch for integrating features
- `feature/xxx`: Feature branches for new features
- `bugfix/xxx`: Bugfix branches for fixing issues
- `release/x.y.z`: Release branches for preparing releases

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/)
specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(parser): add support for artist criteria

Add support for filtering tracks by artist in the query parser.
This allows users to create playlists with tracks from specific artists.

Closes #42
```

## Pull Request Process

1. **Create a branch** from `develop` for your changes
2. **Make your changes** and commit them with descriptive commit messages
3. **Write or update tests** to cover your changes
4. **Update documentation** if necessary
5. **Run the test suite** to ensure all tests pass
6. **Push your branch** to your fork
7. **Create a pull request** to the `develop` branch
8. **Address review comments** if any

### Pull Request Template

```markdown
## Description
[Describe the changes you've made]

## Related Issue
[Link to the related issue, if applicable]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
[Describe the tests you ran]

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

## Issue Reporting

### Bug Reports

When reporting a bug, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: Python version, OS, package version, etc.
6. **Additional Context**: Any other relevant information

### Feature Requests

When requesting a feature, please include:

1. **Description**: Clear description of the feature
2. **Use Case**: Why this feature would be useful
3. **Proposed Solution**: If you have ideas on how to implement it
4. **Alternatives**: Any alternative solutions you've considered

## Code of Conduct

Please note that this project is released with a [Contributor Code of
Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to
abide by its terms.

## License

By contributing to mkplaylist, you agree that your contributions will be
licensed under the project's license.

## Questions?

If you have any questions or need help, feel free to:

- Open an issue with the "question" label
- Reach out to the maintainers directly

Thank you for contributing to mkplaylist!
