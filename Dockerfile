# .github/workflows/ci.yml
# LLM OS CI/CD 파이프라인

name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  release:
    types: [ published ]

jobs:
  # 코드 품질 검사
  lint:
    name: Code Quality
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
          
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install black flake8 mypy pytest
        
    - name: Run Black (Code Formatting)
      run: black --check --diff src/ tests/
      
    - name: Run Flake8 (Linting)
      run: flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
      
    - name: Run MyPy (Type Checking)
      run: mypy src/ --ignore-missing-imports

  # 테스트 실행
  test:
    name: Test Suite
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']
        
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-${{ matrix.python-version }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-${{ matrix.python-version }}-pip-
          
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock
        
    - name: Run tests
      env:
        OPENAI_API_KEY: test-key
        ANTHROPIC_API_KEY: test-key
        GOOGLE_API_KEY: test-key
        LLMOS_TEST_MODE: true
      run: |
        pytest tests/ --cov=src/llmos --cov-report=xml --cov-report=term-missing
        
    - name: Upload coverage to Codecov
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.9'
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  # 보안 검사
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit
        
    - name: Run Safety (Dependency Security)
      run: safety check --json || true
      
    - name: Run Bandit (Code Security)
      run: bandit -r src/ -f json || true

  # 빌드 테스트
  build:
    name: Build Test
    runs-on: ubuntu-latest
    needs: [lint, test]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
        
    - name: Build package
      run: python -m build
      
    - name: Check package
      run: twine check dist/*
      
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/

  # 도커 이미지 빌드
  docker:
    name: Docker Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: Login to DockerHub
      if: github.event_name != 'pull_request'
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: llmos/llmos
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  # 배포 (릴리즈 시에만)
  deploy:
    name: Deploy to PyPI
    runs-on: ubuntu-latest
    needs: [lint, test, build]
    if: github.event_name == 'release' && github.event.action == 'published'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
        
    - name: Build package
      run: python -m build
      
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*

  # 알림
  notify:
    name: Notification
    runs-on: ubuntu-latest
    needs: [lint, test, build]
    if: always()
    
    steps:
    - name: Notify success
      if: needs.lint.result == 'success' && needs.test.result == 'success' && needs.build.result == 'success'
      run: |
        echo "✅ All checks passed successfully!"
        
    - name: Notify failure
      if: needs.lint.result == 'failure' || needs.test.result == 'failure' || needs.build.result == 'failure'
      run: |
        echo "❌ Some checks failed. Please review the logs."
        exit 1