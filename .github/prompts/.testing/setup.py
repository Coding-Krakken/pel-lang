#!/usr/bin/env python3
"""
Setup script for LLM Prompt Testing Framework
"""

import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is sufficient"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    requirements_path = Path(__file__).parent / 'requirements.txt'

    import subprocess
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_env_file():
    """Setup .env file if it doesn't exist"""
    print("\n🔑 Setting up environment file...")
    env_path = Path(__file__).parent / '.env'
    env_example_path = Path(__file__).parent / '.env.example'

    if env_path.exists():
        print("⚠️  .env file already exists, skipping...")
        return True

    try:
        with open(env_example_path) as src:
            with open(env_path, 'w') as dst:
                dst.write(src.read())
        print("✅ Created .env file from template")
        print("⚠️  IMPORTANT: Edit .testing/.env and add your API keys!")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_results_dir():
    """Create results directory"""
    print("\n📁 Creating results directory...")
    results_path = Path(__file__).parent / 'results'
    results_path.mkdir(exist_ok=True)
    print("✅ Results directory ready")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing module imports...")

    modules = [
        'yaml',
        'openai',
        'anthropic',
        'jsonschema',
        'dotenv',
        'colorama',
        'tabulate',
        'jinja2'
    ]

    failed = []
    for module in modules:
        try:
            __import__(module.replace('-', '_'))
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed.append(module)

    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("   Try running: pip install -r .testing/requirements.txt")
        return False

    return True

def main():
    """Run setup"""
    print("=" * 60)
    print("LLM Prompt Testing Framework - Setup")
    print("=" * 60)

    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_env_file),
        ("Creating directories", create_results_dir),
        ("Testing imports", test_imports),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("  1. Edit .testing/.env and add your API keys")
    print("  2. Run a test: npm test path/to/prompt.md")
    print("  3. Check .testing/QUICKSTART.md for more info")
    print()

if __name__ == '__main__':
    main()
