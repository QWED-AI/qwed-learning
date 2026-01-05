# Contributing to QWED Learning

Thank you for your interest in contributing to the QWED Learning course! 🎓

This course teaches developers how to build trustworthy AI systems using deterministic verification.

## 🎯 How You Can Help

### 1. **Fix Typos or Improve Clarity**

Found a typo or confusing explanation?

**Steps:**
1. Fork the repo
2. Fix the issue
3. Submit a Pull Request

**Example PR title:** `docs: Fix typo in Module 2 - symbolic engine explanation`

### 2. **Add Code Examples**

Have a great verification use case?

**What we're looking for:**
- Real-world production examples
- Different industries (healthcare, finance, legal, etc.)
- Integration with popular frameworks

**Guidelines:**
- Add to `module-3-hands-on/examples/` or `module-4-advanced/examples/`
- Include docstrings and comments
- Follow existing code style
- Add usage example at bottom

**Example structure:**
```python
"""
Brief description of what this example demonstrates.

Use Case: Where this would be used in production
"""

from qwed_sdk import QWEDLocal

# Your example code here

if __name__ == "__main__":
    # Demo usage
    pass
```

### 3. **Improve Exercises**

Better practice exercises help students learn!

**Guidelines:**
- Make exercises progressively challenging
- Include solutions in `<details>` tags
- Provide clear learning objectives

### 4. **Translate Content**

Help non-English speakers learn verification!

**Process:**
1. Create `{language-code}/` folder (e.g., `es/`, `fr/`, `hi/`)
2. Translate module READMEs
3. Keep code examples in English (universal language of code)
4. Submit PR

### 5. **Report Issues**

Found a bug or have a suggestion?

[Open an issue](https://github.com/QWED-AI/qwed-learning/issues/new)

**Use these labels:**
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `question` - Need clarification
- `good first issue` - Great for newcomers

---

## 📋 Contribution Guidelines

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep functions focused (single responsibility)

**Markdown:**
- Use clear headers (`##`, `###`)
- Add code syntax highlighting
- Keep paragraphs short (3-4 lines max)
- Use bullet points for lists

### Commit Message Format

```
<type>: <description>

[optional body]
```

**Types:**
- `feat`: New feature (new module, example, etc.)
- `fix`: Bug fix
- `docs`: Documentation only changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add LlamaIndex integration example

docs: Improve Module 3 error handling section

fix: Correct compound interest formula in financial_calculator.py
```

### Pull Request Process

1. **Fork & Create Branch**
   ```bash
   git clone https://github.com/YOUR-USERNAME/qwed-learning.git
   cd qwed-learning
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, documented code
   - Test your changes locally
   - Update relevant documentation

3. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

4. **Submit PR**
   - Go to GitHub and create Pull Request
   - Describe what you changed and why
   - Reference any related issues

5. **Review Process**
   - Maintainers will review your PR
   - Address any feedback
   - Once approved, it will be merged!

---

## 🚫 What NOT to Contribute

**Please avoid:**
- ❌ Promotional content or spam
- ❌ Unrelated code examples
- ❌ Breaking changes without discussion
- ❌ Copyrighted material without permission

---

## 💡 Getting Help

**Stuck or have questions?**

- 💬 [GitHub Discussions](https://github.com/QWED-AI/qwed-learning/discussions)
- 📧 Email: rahul@qwedai.com
- 🐦 Twitter: [@rahuldass29](https://x.com/rahuldass29)

---

## 🌟 Recognition

Contributors will be:
- Listed in our README
- Thanked on Twitter
- Given credit in release notes

**Top contributors may receive:**
- Early access to new QWED features
- Invitation to maintainer team
- Swag (when available)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the CC0-1.0 License (same as the project).

---

## 🙏 Thank You!

Every contribution makes this course better for developers worldwide. Your help is truly appreciated! 🎉

**Let's build trustworthy AI together!**
