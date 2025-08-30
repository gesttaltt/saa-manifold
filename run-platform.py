#!/usr/bin/env python3
"""
SAA Manifold Research Platform - Intelligent Runner
Automatically detects system capabilities and runs the optimal configuration.
"""

import os
import sys
import subprocess
import platform
import json
import time
import signal
import socket
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def find_free_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find free port in range {start_port}-{start_port + max_attempts}")

class PlatformCapabilities:
    """Detect and manage system capabilities for optimal platform configuration."""
    
    def __init__(self):
        self.system_info = {
            "os": platform.system(),
            "arch": platform.machine(),
            "python_version": platform.python_version(),
        }
        self.capabilities = self._detect_capabilities()
        self.ports = self._allocate_ports()
    
    def _detect_capabilities(self) -> Dict[str, bool]:
        """Detect system capabilities for optimal configuration."""
        caps = {
            "python3": self._check_python(),
            "nodejs": self._check_nodejs(),
            "docker": self._check_docker(),
            "gpu_nvidia": self._check_nvidia_gpu(),
            "git": self._check_git(),
            "sufficient_memory": self._check_memory(),
        }
        
        # Derived capabilities - Fix GPU acceleration logic
        caps["enhanced_mode"] = caps["docker"] and caps["sufficient_memory"]
        caps["gpu_acceleration"] = caps["gpu_nvidia"]  # GPU acceleration doesn't require Docker
        caps["development_mode"] = caps["python3"] and caps["nodejs"] and caps["git"]
        
        return caps
    
    def _allocate_ports(self) -> Dict[str, int]:
        """Allocate free ports for all services."""
        try:
            backend_port = find_free_port(8000)
            frontend_port = find_free_port(3000)
            docs_port = find_free_port(8080)
            
            return {
                "backend": backend_port,
                "frontend": frontend_port,
                "docs": docs_port,
                "postgres": find_free_port(5432),
                "redis": find_free_port(6379)
            }
        except RuntimeError as e:
            print(f"⚠️  Port allocation failed: {e}")
            # Use default ports as fallback
            return {
                "backend": 8000,
                "frontend": 3000,
                "docs": 8080,
                "postgres": 5432,
                "redis": 6379
            }
    
    def _check_python(self) -> bool:
        """Check Python 3.11+ availability."""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            version = result.stdout.strip().split()[1]
            major, minor = map(int, version.split('.')[:2])
            return major >= 3 and minor >= 11
        except:
            return False
    
    def _check_nodejs(self) -> bool:
        """Check Node.js 18+ availability."""
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True)
            version = result.stdout.strip().replace('v', '')
            major = int(version.split('.')[0])
            return major >= 18
        except:
            return False
    
    def _check_docker(self) -> bool:
        """Check Docker availability."""
        try:
            # Try docker command
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return False
                
            # Also check if Docker daemon is running
            result = subprocess.run(["docker", "info"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def _check_nvidia_gpu(self) -> bool:
        """Check NVIDIA GPU availability."""
        try:
            result = subprocess.run(["nvidia-smi"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_git(self) -> bool:
        """Check Git availability."""
        try:
            result = subprocess.run(["git", "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_memory(self) -> bool:
        """Check if system has sufficient memory (8GB+)."""
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            return memory_gb >= 8.0
        except:
            # Assume sufficient if we can't check
            return True
    
    def print_capabilities(self):
        """Print system capabilities assessment."""
        print("🔍 System Capabilities Assessment:")
        print("=" * 50)
        
        status_map = {True: "✅", False: "❌"}
        
        for cap, available in self.capabilities.items():
            status = status_map[available]
            cap_name = cap.replace('_', ' ').title()
            print(f"{status} {cap_name}: {'Available' if available else 'Not Available'}")
        
        print(f"\n🔌 Allocated Ports:")
        for service, port in self.ports.items():
            print(f"   {service.title()}: {port}")
        
        print("\n🎯 Recommended Configuration:")
        if self.capabilities["enhanced_mode"]:
            print("   📦 Enhanced Mode (Docker + Full Features)")
        elif self.capabilities["development_mode"]:
            print("   🛠️  Development Mode (Local Python + Node)")
        else:
            print("   📝 Documentation Mode (Limited functionality)")

class PlatformRunner:
    """Intelligent platform runner that adapts to system capabilities."""
    
    def __init__(self):
        self.capabilities = PlatformCapabilities()
        self.processes: List[subprocess.Popen] = []
        self.project_root = Path(__file__).parent
    
    def run(self):
        """Run the platform with optimal configuration."""
        print("🚀 SAA Manifold Research Platform")
        print("=" * 50)
        
        self.capabilities.print_capabilities()
        print()
        
        # Choose and execute run strategy
        if self.capabilities.capabilities["enhanced_mode"]:
            self._run_enhanced_mode()
        elif self.capabilities.capabilities["development_mode"]:
            self._run_development_mode()
        else:
            self._run_documentation_mode()
    
    def _run_enhanced_mode(self):
        """Run in enhanced mode with Docker and all features."""
        print("🚀 Starting Enhanced Mode...")
        
        try:
            # Create .env file if it doesn't exist
            self._setup_environment()
            
            # Start with Docker Compose
            cmd = ["docker-compose", "up", "--build"]
            if self.capabilities.capabilities["gpu_nvidia"]:
                cmd.extend(["--profile", "gpu"])
            
            print("📦 Starting services with Docker Compose...")
            process = subprocess.Popen(cmd, cwd=self.project_root)
            self.processes.append(process)
            
            # Print access information
            self._print_access_info()
            
            # Wait for user interruption
            self._wait_for_exit()
            
        except KeyboardInterrupt:
            self._cleanup()
        except Exception as e:
            print(f"❌ Enhanced mode failed: {e}")
            print("   Falling back to development mode...")
            self._run_development_mode()
    
    def _run_development_mode(self):
        """Run in development mode with local processes."""
        print("🛠️  Starting Development Mode...")
        
        try:
            # Setup environment
            self._setup_environment()
            
            # Start backend
            backend_process = self._start_backend()
            if backend_process:
                self.processes.append(backend_process)
                print("✅ Backend started on http://localhost:8000")
            
            # Start frontend
            frontend_process = self._start_frontend()
            if frontend_process:
                self.processes.append(frontend_process)
                print("✅ Frontend started on http://localhost:3000")
            
            # Print access information
            self._print_access_info()
            
            # Wait for user interruption
            self._wait_for_exit()
            
        except KeyboardInterrupt:
            self._cleanup()
        except Exception as e:
            print(f"❌ Development mode failed: {e}")
            self._run_documentation_mode()
    
    def _run_documentation_mode(self):
        """Run documentation server only."""
        print("📚 Starting Documentation Mode...")
        print("   Limited functionality - install Python 3.11+ and Node.js 18+ for full features")
        
        # Try to serve documentation
        try:
            # Simple HTTP server for documentation
            docs_path = self.project_root / "docs"
            if docs_path.exists():
                cmd = [sys.executable, "-m", "http.server", "8080"]
                process = subprocess.Popen(cmd, cwd=docs_path)
                self.processes.append(process)
                
                print("✅ Documentation server started on http://localhost:8080")
                self._wait_for_exit()
        except Exception as e:
            print(f"❌ Could not start documentation server: {e}")
            print("   Please open docs/README.md manually")
    
    def _setup_environment(self):
        """Setup environment variables and configuration."""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            print("📝 Creating .env file from template...")
            
            # Copy .env.example to .env with capability-based defaults
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                content = src.read()
                
                # Adjust settings based on capabilities
                if not self.capabilities.capabilities["gpu_nvidia"]:
                    content = content.replace("GPU_ENABLED=true", "GPU_ENABLED=false")
                
                if not self.capabilities.capabilities["enhanced_mode"]:
                    content = content.replace("AI_ENABLED=true", "AI_ENABLED=false")
                    content = content.replace("STREAMING_ENABLED=true", "STREAMING_ENABLED=false")
                
                dst.write(content)
    
    def _start_backend(self) -> Optional[subprocess.Popen]:
        """Start the backend API server."""
        backend_dir = self.project_root / "backend"
        
        if not backend_dir.exists():
            print("❌ Backend directory not found")
            return None
        
        try:
            backend_port = self.capabilities.ports["backend"]
            
            # Setup virtual environment
            venv_dir = backend_dir / "venv"
            if not venv_dir.exists():
                print("📦 Creating Python virtual environment...")
                subprocess.run([sys.executable, "-m", "venv", "venv"], 
                             cwd=backend_dir, check=True)
            
            # Determine correct paths for current OS
            if self.capabilities.system_info["os"] == "Windows":
                pip_cmd = venv_dir / "Scripts" / "pip.exe"
                python_cmd = venv_dir / "Scripts" / "python.exe"
            else:
                pip_cmd = venv_dir / "bin" / "pip"
                python_cmd = venv_dir / "bin" / "python"
            
            # Check if commands exist
            if not pip_cmd.exists():
                print(f"❌ Pip not found at {pip_cmd}")
                return None
            
            print("📦 Installing Python dependencies...")
            # Install minimal dependencies if requirements.txt doesn't exist
            requirements_file = backend_dir / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([str(pip_cmd), "install", "-r", "requirements.txt"], 
                             cwd=backend_dir, check=True, capture_output=True)
            else:
                # Install minimal dependencies
                subprocess.run([str(pip_cmd), "install", "fastapi", "uvicorn", "numpy", "scipy"], 
                             cwd=backend_dir, check=True, capture_output=True)
            
            # Start server with dynamic port
            print(f"🔄 Starting backend server on port {backend_port}...")
            cmd = [str(python_cmd), "-m", "uvicorn", "src.main:app", 
                   "--reload", "--host", "0.0.0.0", "--port", str(backend_port)]
            
            return subprocess.Popen(cmd, cwd=backend_dir)
            
        except Exception as e:
            print(f"❌ Backend startup failed: {e}")
            return None
    
    def _start_frontend(self) -> Optional[subprocess.Popen]:
        """Start the frontend development server."""
        frontend_dir = self.project_root / "frontend"
        
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return None
        
        try:
            frontend_port = self.capabilities.ports["frontend"]
            backend_port = self.capabilities.ports["backend"]
            
            # Check if npm is available
            try:
                subprocess.run(["npm", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ npm not found. Please install Node.js")
                return None
            
            # Install dependencies
            package_json = frontend_dir / "package.json"
            if package_json.exists():
                print("📦 Installing Node.js dependencies...")
                subprocess.run(["npm", "install"], cwd=frontend_dir, 
                             check=True, capture_output=True, timeout=300)
            else:
                print("⚠️  No package.json found, skipping npm install")
            
            # Create minimal package.json if it doesn't exist
            if not package_json.exists():
                minimal_package = {
                    "name": "saa-frontend",
                    "version": "1.0.0",
                    "scripts": {
                        "dev": "python -m http.server 3000"
                    }
                }
                with open(package_json, 'w') as f:
                    json.dump(minimal_package, f, indent=2)
            
            # Set environment variables for API connection
            env = os.environ.copy()
            env["VITE_API_BASE_URL"] = f"http://localhost:{backend_port}/api/v1"
            env["PORT"] = str(frontend_port)
            
            # Start development server
            print(f"🔄 Starting frontend server on port {frontend_port}...")
            
            # Try npm run dev first, fallback to simple server
            try:
                return subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir, env=env)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  npm run dev failed, starting simple HTTP server...")
                # Fallback to simple Python HTTP server
                return subprocess.Popen([
                    sys.executable, "-m", "http.server", str(frontend_port)
                ], cwd=frontend_dir)
            
        except Exception as e:
            print(f"❌ Frontend startup failed: {e}")
            return None
    
    def _print_access_info(self):
        """Print access information for the user."""
        frontend_port = self.capabilities.ports["frontend"]
        backend_port = self.capabilities.ports["backend"]
        
        print("\n" + "=" * 50)
        print("🌐 SAA Platform Access Points:")
        print(f"   Frontend:      http://localhost:{frontend_port}")
        print(f"   Backend API:   http://localhost:{backend_port}")
        print(f"   API Docs:      http://localhost:{backend_port}/docs")
        print(f"   Health Check:  http://localhost:{backend_port}/health")
        
        if self.capabilities.capabilities["enhanced_mode"]:
            print(f"   GPU Dashboard: http://localhost:{frontend_port}/monitoring")
            print(f"   AI Assistant:  http://localhost:{frontend_port}/ai")
            print(f"   Collaboration: http://localhost:{frontend_port}/collaborate")
        
        print("\n🎯 Quick Actions:")
        print("   1. Visit Frontend → Analysis → Start New Analysis")
        print("   2. Configure region (default SAA core)")
        print("   3. View results in 3D Visualization")
        
        if self.capabilities.capabilities["gpu_acceleration"]:
            print("   4. ⚡ GPU acceleration available")
        
        print("\n⚠️  Press Ctrl+C to stop all services")
        print("=" * 50)
    
    def _wait_for_exit(self):
        """Wait for user to stop the platform."""
        try:
            while True:
                time.sleep(1)
                # Check if any process has died
                for process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️  Process {process.pid} has stopped")
        except KeyboardInterrupt:
            pass
    
    def _cleanup(self):
        """Cleanup all running processes."""
        print("\n🛑 Stopping SAA Platform...")
        
        for process in self.processes:
            try:
                if process.poll() is None:  # Still running
                    process.terminate()
                    # Give process time to cleanup
                    try:
                        process.wait(timeout=5)
                        print(f"✅ Process {process.pid} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        print(f"🔥 Process {process.pid} force killed")
            except Exception as e:
                print(f"⚠️  Error stopping process {process.pid}: {e}")
        
        print("✅ All services stopped")

def main():
    """Main entry point for platform runner."""
    print("🧬 SAA Manifold Research Platform")
    print("   Intelligent Scientific Computing Platform")
    print()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--capabilities":
            runner = PlatformRunner()
            runner.capabilities.print_capabilities()
            return
        elif sys.argv[1] == "--help":
            print_help()
            return
        elif sys.argv[1] == "--simple":
            run_simple_mode()
            return
    
    # Run with capability detection
    runner = PlatformRunner()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Received interrupt signal...")
        runner._cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        runner.run()
    except Exception as e:
        print(f"❌ Platform failed to start: {e}")
        print("   Try running with --simple flag for basic functionality")
        sys.exit(1)

def run_simple_mode():
    """Run in simple mode - just the original Python visualization."""
    print("🔬 Starting Simple SAA Visualization...")
    
    try:
        # Check if original script exists
        original_script = Path("saa_manifold.py")
        if original_script.exists():
            print("✅ Running original SAA manifold visualization...")
            subprocess.run([sys.executable, str(original_script)])
        else:
            print("❌ Original saa_manifold.py not found")
            print("   Run without --simple flag for full platform")
    except Exception as e:
        print(f"❌ Simple mode failed: {e}")

def print_help():
    """Print help information."""
    help_text = """
SAA Manifold Research Platform Runner

USAGE:
    python run-platform.py [OPTIONS]

OPTIONS:
    --help          Show this help message
    --capabilities  Show system capabilities assessment
    --simple        Run original simple visualization only

AUTOMATIC MODES:
    Enhanced Mode   - Full features with Docker (if available)
    Development Mode - Local Python + Node.js (if available)  
    Documentation   - Read-only documentation server

EXAMPLES:
    python run-platform.py                    # Auto-detect best mode
    python run-platform.py --capabilities     # Check system capabilities
    python run-platform.py --simple           # Run basic visualization only

ACCESS POINTS:
    Frontend:    http://localhost:3000
    Backend:     http://localhost:8000  
    API Docs:    http://localhost:8000/docs
    Health:      http://localhost:8000/health

For more information, see docs/development/setup.md
"""
    print(help_text)

if __name__ == "__main__":
    main()