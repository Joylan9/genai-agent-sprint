# CI/CD and Local Quality Checks

Ensuring code quality at every step:
- Local Linting: Run flake8 or black to maintain style consistency.
- Security Scanning: Use Bandit or safety to detect vulnerabilities in dependencies.
- Unit Tests: Fast feedback loop with pytest for core logic.
- CI Pipeline: Automated execution of full test suite on every pull request.
- Artifacts: Build and push Docker images only after all checks pass.
