# Prerequisites and Installation

[← Previous: Introduction](./01-introduction.md) | [Home](../README.md) | [Next: Configuration →](./03-configuration.md)

---

## System Requirements

**Minimum Requirements:**
- Python 3.11 or higher
- 4GB RAM
- 10GB available disk space
- Internet connection for package installation

**Recommended for Production:**
- Python 3.11+
- 8GB+ RAM
- 50GB+ SSD storage
- Redis server
- PostgreSQL database

## Required Software

Before installing the foundation, ensure you have these components installed:

### 1. Python Installation

**Windows:**
1. Download Python from [python.org](https://python.org)
2. Run installer with "Add Python to PATH" checked
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
python3.11 --version
```

### 2. Redis Installation (Recommended)

**Windows:**
1. Download Redis from [GitHub releases](https://github.com/microsoftarchive/redis/releases)
2. Install and start Redis service
3. Test: `redis-cli ping` (should return "PONG")

**macOS:**
```bash
brew install redis
brew services start redis
redis-cli ping
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
redis-cli ping
```

### 3. PostgreSQL (Production)

**Windows:**
1. Download from [postgresql.org](https://postgresql.org)
2. Install with default settings
3. Remember the superuser password

**macOS:**
```bash
brew install postgresql
brew services start postgresql
createdb foundation_db
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Foundation Installation

### Step 1: Clone or Download the Foundation

```bash
# If using Git
git clone <repository-url> enterprise-saas-foundation
cd enterprise-saas-foundation

# Or download and extract ZIP file
```

### Step 2: Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your command prompt, indicating the virtual environment is active.

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install foundation dependencies
pip install -r requirements.txt
```

**Common Installation Issues:**
- If you get permission errors, ensure you're in the virtual environment
- For compilation errors on Windows, install Microsoft Visual C++ Build Tools
- On macOS, you may need Xcode command line tools: `xcode-select --install`

---

**Navigation**: [← Previous: Introduction](./01-introduction.md) | [Top ↑](#) | [Next: Configuration →](./03-configuration.md)

