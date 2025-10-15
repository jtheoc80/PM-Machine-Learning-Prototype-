# Contributing to Pressure Relief Valve LLM Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check if the issue already exists in the [Issues](https://github.com/jtheoc80/PM-Machine-Learning-Prototype-/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)

### Contributing Code

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/PM-Machine-Learning-Prototype-.git
   cd PM-Machine-Learning-Prototype-
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test Your Changes**
   ```bash
   python validate.py
   python demo.py
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Documentation

- Update README.md if adding new features
- Update TESTING.md if adding new tests
- Add comments for complex algorithms
- Include usage examples

### Testing

Before submitting:

- Run `python validate.py` for basic checks
- Test with different file formats
- Test interactive mode
- Test API endpoints if modified

### Commit Messages

Use clear, descriptive commit messages:

- `feat: Add support for Excel file upload`
- `fix: Resolve memory leak in vector store`
- `docs: Update installation instructions`
- `test: Add unit tests for data processor`

## Areas for Contribution

### High Priority

- [ ] Add support for more file formats (Excel, PDF, Word)
- [ ] Implement fine-tuning capabilities
- [ ] Add GPU acceleration support
- [ ] Improve error handling and logging
- [ ] Add unit tests

### Medium Priority

- [ ] Create web interface (HTML/JavaScript)
- [ ] Add more pre-built queries
- [ ] Improve documentation with examples
- [ ] Add data visualization features
- [ ] Support for multiple languages

### Nice to Have

- [ ] Docker containerization
- [ ] Cloud deployment guides
- [ ] Integration with popular data sources
- [ ] Advanced search and filtering
- [ ] User authentication for API

## Questions?

If you have questions about contributing:

1. Check existing documentation (README.md, TESTING.md)
2. Look at closed Pull Requests for examples
3. Open an issue with the question label
4. Reach out to maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Acknowledged in commits

Thank you for contributing to make this project better!
