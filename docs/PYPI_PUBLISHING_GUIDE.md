# Publishing Loggerheads to PyPI

This guide walks you through publishing the loggerheads package to PyPI so users can install it with `pip install loggerheads`.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account** (optional but recommended): Create at https://test.pypi.org/account/register/
3. **API Token**: Generate from https://pypi.org/manage/account/token/
   - Save the token securely - you'll only see it once!

## Step 1: Configure PyPI Credentials

Create or update `~/.pypirc`:

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-ACTUAL-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
EOF

chmod 600 ~/.pypirc
```

Replace `pypi-YOUR-ACTUAL-TOKEN-HERE` with your actual PyPI API token.

## Step 2: Test Upload (Recommended)

First upload to TestPyPI to verify everything works:

```bash
cd /Users/mitch_1/daily_log_ai

# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

Visit https://test.pypi.org/project/loggerheads/ to verify it looks correct.

Test installation from TestPyPI:

```bash
pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple loggerheads
```

(Note: `--extra-index-url` allows installing dependencies from main PyPI)

## Step 3: Upload to Real PyPI

Once you've verified everything works on TestPyPI:

```bash
cd /Users/mitch_1/daily_log_ai

# Upload to PyPI
twine upload dist/*
```

You'll see:

```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading loggerheads-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.0/62.0 kB • 00:01
Uploading loggerheads-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60.0/60.0 kB • 00:01

View at:
https://pypi.org/project/loggerheads/1.0.0/
```

## Step 4: Verify Installation

Test that users can now install it:

```bash
# In a clean environment
pip3 install loggerheads

# Verify it works
loggerheads --help
```

## Updating the Package

When you make changes and want to release a new version:

1. **Update version** in `setup.py`:
   ```python
   version="1.0.1",  # Increment version
   ```

2. **Clean old builds**:
   ```bash
   rm -rf build dist *.egg-info
   ```

3. **Build new packages**:
   ```bash
   python3 setup.py sdist bdist_wheel
   ```

4. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

## Version Numbering

Follow semantic versioning (semver):

- **1.0.0** → **1.0.1**: Bug fixes, minor changes
- **1.0.0** → **1.1.0**: New features, backward compatible
- **1.0.0** → **2.0.0**: Breaking changes

## Troubleshooting

### "The user '\_\_token\_\_' isn't allowed to upload"

- Wrong API token or token doesn't have upload permissions
- Generate new token at https://pypi.org/manage/account/token/

### "File already exists"

- You've already uploaded this version
- Increment version number in setup.py and rebuild

### "Invalid distribution"

- Run `twine check dist/*` to see specific errors
- Fix issues in setup.py or README.md

### "HTTPError 403: Invalid or non-existent authentication information"

- Check ~/.pypirc credentials
- Ensure API token is correct

## Alternative: Manual Upload via Web UI

If you prefer not to use the command line:

1. Go to https://pypi.org/manage/projects/
2. Click "Upload distribution"
3. Upload both files:
   - `dist/loggerheads-1.0.0-py3-none-any.whl`
   - `dist/loggerheads-1.0.0.tar.gz`

## What Happens After Upload?

Once uploaded to PyPI:

1. **Package is public** - Anyone can install with `pip install loggerheads`
2. **PyPI hosts files** - Distributed via CDN globally
3. **Can't delete** - You can only "yank" versions (hide but still installable)
4. **Update anytime** - Just increment version and re-upload

## Quick Reference

```bash
# Build package
python3 setup.py sdist bdist_wheel

# Check package
twine check dist/*

# Upload to TestPyPI (testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*

# Test install
pip3 install loggerheads
```

## Resources

- PyPI Documentation: https://packaging.python.org/tutorials/packaging-projects/
- Twine Documentation: https://twine.readthedocs.io/
- Semantic Versioning: https://semver.org/
