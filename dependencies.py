import subprocess
import sys

# List of dependencies
dependencies = {
    "win32gui": "pywin32",
    "socket": None,  # Built-in module
    "threading": None,  # Built-in module
    "datetime": None,  # Built-in module
    "os": None,  # Built-in module
    "argparse": None,  # Built-in module
    "re": None,
}

def install_package(package_name):
    """Install a package using pip."""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    except Exception as e:
        print(f"Failed to install {package_name}: {e}")

def check_dependencies():
    """Check and install missing dependencies."""
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"{module}: OK")
        except ImportError:
            if package:
                print(f"{module} is missing. Installing {package}...")
                install_package(package)
            else:
                print(f"{module} is a built-in module. No installation required.")

if __name__ == "__main__":
    print("Checking dependencies...")
    check_dependencies()
    print("All dependencies are satisfied.")
