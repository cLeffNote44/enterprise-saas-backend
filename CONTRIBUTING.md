# Contributing to Enterprise SaaS Backend

First off, thank you for considering contributing to Enterprise SaaS Backend! It's people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title** for the issue
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs** if possible
* **Include your environment details** (OS, Python version, Docker version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title** for the issue
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior** and **explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `develop`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the style guidelines
6. Issue that pull request!

## Development Process

### Setting Up Your Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/enterprise-saas-backend.git
   cd enterprise-saas-backend
   ```

2. **Set Up Environment**
   ```bash
   cp .env.docker.example .env
   docker compose up -d
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Code Style Guidelines

#### Python Code Style

We use Black, isort, and Flake8 for Python code formatting and linting:

```bash
# Format code
black foundation/
isort foundation/

# Check linting
flake8 foundation/
```

**Key Guidelines:**
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use descriptive variable and function names
- Write docstrings for all functions, classes, and modules

#### Django Best Practices

- Keep business logic in services, not views
- Use Django's built-in features when possible
- Write comprehensive tests for all new features
- Use migrations for all database changes
- Follow the fat models, thin views, stupid templates principle

#### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

**Example:**
```
Add user authentication via JWT

- Implement JWT token generation
- Add authentication middleware
- Update API documentation
- Add comprehensive test coverage

Fixes #123
```

### Testing

All new features must include tests. We aim for >80% code coverage.

```bash
# Run tests locally
docker compose exec web sh -c "cd foundation && python manage.py test"

# Run with coverage
docker compose exec web sh -c "cd foundation && coverage run --source='.' manage.py test && coverage report"
```

**Test Guidelines:**
- Write unit tests for all business logic
- Write integration tests for API endpoints
- Use factories instead of fixtures when possible
- Mock external services in tests
- Test both success and failure cases

### Documentation

- Update README.md if you change setup or configuration
- Update API documentation for any API changes
- Add docstrings to all new functions and classes
- Include type hints for better code documentation
- Update CHANGELOG.md with your changes

### Pull Request Process

1. **Update Documentation** - Ensure README.md and other docs reflect your changes
2. **Add Tests** - Cover new functionality with tests
3. **Pass CI** - Ensure all GitHub Actions checks pass
4. **Code Review** - Address reviewer feedback promptly
5. **Squash Commits** - Clean up commit history before merge

### Release Process

We use Semantic Versioning (SemVer):

- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality additions
- PATCH version for backwards-compatible bug fixes

## Project Structure

```
enterprise-saas-backend/
├── foundation/              # Main Django project
│   ├── foundation/         # Project configuration
│   │   ├── apps/          # Django applications
│   │   ├── config/        # Settings and configuration
│   │   └── admin/         # Admin customizations
│   └── manage.py
├── requirements/           # Python dependencies
├── scripts/               # Helper scripts
├── docs/                  # Documentation
├── tests/                 # Test suites
└── docker-compose.yml     # Docker configuration
```

## API Development Guidelines

### RESTful Principles

- Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Return appropriate status codes
- Use consistent URL patterns
- Version your APIs (/api/v1/)
- Implement pagination for list endpoints

### API Documentation

All APIs must be documented using drf-spectacular:

```python
from drf_spectacular.utils import extend_schema

@extend_schema(
    summary="Create a new user",
    description="Create a new user with the provided data",
    request=UserSerializer,
    responses={201: UserSerializer},
    tags=["users"]
)
def create_user(request):
    ...
```

## Security Guidelines

- Never commit secrets or credentials
- Use environment variables for configuration
- Implement proper authentication and authorization
- Validate all user inputs
- Use HTTPS in production
- Keep dependencies updated
- Run security scans regularly

## Questions?

Feel free to open an issue with your question or reach out to the maintainers directly.

## Recognition

Contributors will be recognized in our README.md file. We appreciate every contribution, no matter how small!

---

Thank you for contributing! 🎉