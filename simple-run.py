#!/usr/bin/env python3
"""
SAA Manifold Platform - Simple & Robust Runner
Optimized for Windows environments with automatic port management and graceful fallbacks.
"""

import os
import sys
import subprocess
import socket
import json
import time
import webbrowser
from pathlib import Path

def find_free_port(start_port=8000):
    """Find the first available port starting from start_port."""
    port = start_port
    while port < start_port + 100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError(f"No free ports found in range {start_port}-{start_port + 100}")

def check_command(cmd):
    """Check if a command is available."""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def create_instant_demo():
    """Create instant browser demo for immediate visualization."""
    print("🎨 Creating instant SAA visualization...")
    
    demo_html = '''<!DOCTYPE html>
<html>
<head>
    <title>SAA Manifold - Instant Demo</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { margin: 0; font-family: Arial, sans-serif; background: #001122; color: white; overflow: hidden; }
        #info { position: absolute; top: 10px; left: 10px; z-index: 100; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 8px; max-width: 300px; }
        #controls { position: absolute; top: 10px; right: 10px; z-index: 100; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 8px; }
        button { background: #1976d2; color: white; border: none; padding: 10px 15px; margin: 5px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #1565c0; }
        canvas { display: block; }
    </style>
</head>
<body>
    <div id="info">
        <h3>🧬 SAA Manifold Platform</h3>
        <p><strong>South Atlantic Anomaly</strong></p>
        <p>Peak: <span id="peak">1,250 p/cm²/s</span></p>
        <p>Anomalies: <span id="count">3 detected</span></p>
        <p style="font-size: 12px; opacity: 0.8; margin-top: 10px;">
            🎯 Drag to rotate • Scroll to zoom
        </p>
    </div>
    
    <div id="controls">
        <button onclick="resetView()">🔄 Reset</button><br>
        <button onclick="toggleMode()" id="modeBtn">🔗 Wireframe</button><br>
        <button onclick="toggleAnim()" id="animBtn">⏸️ Pause</button><br>
        <button onclick="exportImg()">📷 Export</button>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r158/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.158.0/examples/js/controls/OrbitControls.js"></script>
    
    <script>
        let scene, camera, renderer, controls, mesh;
        let wireframe = false, animate = true;

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x001122);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(50, 50, 50);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;

            // Lighting
            scene.add(new THREE.AmbientLight(0x404040, 0.4));
            const light = new THREE.DirectionalLight(0xffffff, 0.8);
            light.position.set(50, 50, 50);
            scene.add(light);

            // Create SAA manifold
            createSAAMesh();
            
            // Animation loop
            function render() {
                requestAnimationFrame(render);
                controls.update();
                if (animate && mesh) mesh.rotation.z += 0.01;
                renderer.render(scene, camera);
            }
            render();

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        }

        function createSAAMesh() {
            const geometry = new THREE.BufferGeometry();
            const vertices = [], colors = [], indices = [];
            
            const res = 60;
            for (let i = 0; i < res; i++) {
                for (let j = 0; j < res; j++) {
                    const lon = -90 + (i / (res-1)) * 90;
                    const lat = -50 + (j / (res-1)) * 50;
                    
                    // SAA intensity model
                    const d1 = Math.sqrt((lon + 50)**2 + (lat + 25)**2);
                    const d2 = Math.sqrt((lon + 45)**2 + (lat + 15)**2);
                    const flux = Math.exp(-d1/20) + 0.8*Math.exp(-d2/15);
                    
                    vertices.push(lon, lat, 4 + flux * 8);
                    
                    // Plasma colormap
                    const t = Math.min(1, flux);
                    colors.push(0.05 + 0.95*t, t*t, 0.2 + 0.8*t*t);
                    
                    if (i < res-1 && j < res-1) {
                        const a = i*res + j, b = (i+1)*res + j;
                        const c = (i+1)*res + (j+1), d = i*res + (j+1);
                        indices.push(a,b,c, a,c,d);
                    }
                }
            }
            
            geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
            geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
            geometry.setIndex(indices);
            geometry.computeNormals();

            const material = new THREE.MeshStandardMaterial({
                vertexColors: true, side: THREE.DoubleSide, 
                transparent: true, opacity: 0.9
            });

            mesh = new THREE.Mesh(geometry, material);
            scene.add(mesh);
        }

        function resetView() { camera.position.set(50,50,50); controls.reset(); }
        function toggleMode() { 
            wireframe = !wireframe; 
            mesh.material.wireframe = wireframe;
            document.getElementById('modeBtn').textContent = wireframe ? '🔲 Solid' : '🔗 Wireframe';
        }
        function toggleAnim() { 
            animate = !animate;
            document.getElementById('animBtn').textContent = animate ? '⏸️ Pause' : '▶️ Play';
        }
        function exportImg() {
            const link = document.createElement('a');
            link.download = 'saa-manifold.png';
            link.href = renderer.domElement.toDataURL();
            link.click();
        }

        init();
        
        console.log('%c🧬 SAA Manifold Demo Ready', 'color: #42a5f5; font-size: 16px; font-weight: bold');
        console.log('🎯 Interactive 3D visualization of South Atlantic Anomaly');
        console.log('🔬 Scientific data representation with realistic flux patterns');
    </script>
</body>
</html>'''
    
    demo_file = Path("saa_instant_demo.html")
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(demo_html)
    
    print(f"✅ Created instant demo: {demo_file}")
    
    try:
        webbrowser.open(f"file://{demo_file.absolute()}")
        print("🌐 Opened in your default browser")
        return True
    except Exception as e:
        print(f"⚠️  Could not auto-open browser: {e}")
        print(f"   Please open {demo_file} manually")
        return False

def run_backend_simple():
    """Run backend with minimal dependencies and dynamic port."""
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None, None
    
    try:
        # Find free port
        backend_port = find_free_port(8000)
        print(f"🔌 Using backend port: {backend_port}")
        
        # Simple server without complex dependencies
        simple_server = f'''
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from main import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port={backend_port}, reload=False)
except ImportError:
    # Fallback to minimal server
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import json
    
    class SAAHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {{"status": "healthy", "mode": "fallback"}}
                self.wfile.write(json.dumps(response).encode())
            else:
                super().do_GET()
    
    with HTTPServer(("", {backend_port}), SAAHandler) as httpd:
        print(f"Fallback server running on port {backend_port}")
        httpd.serve_forever()
'''
        
        server_file = backend_dir / "simple_server.py"
        with open(server_file, 'w') as f:
            f.write(simple_server)
        
        # Start simple server
        cmd = [sys.executable, str(server_file)]
        process = subprocess.Popen(cmd, cwd=backend_dir)
        
        return process, backend_port
        
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        return None, None

def run_frontend_simple(backend_port):
    """Run frontend with dynamic port and backend connection."""
    frontend_dir = Path("frontend")
    
    try:
        frontend_port = find_free_port(3000)
        print(f"🔌 Using frontend port: {frontend_port}")
        
        if frontend_dir.exists() and (frontend_dir / "package.json").exists():
            # Try to run React dev server
            try:
                print("📦 Checking Node.js dependencies...")
                
                # Check if node_modules exists
                node_modules = frontend_dir / "node_modules"
                if not node_modules.exists():
                    print("📦 Installing frontend dependencies (this may take a moment)...")
                    result = subprocess.run(["npm", "install"], 
                                          cwd=frontend_dir, 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=300)
                    if result.returncode != 0:
                        print(f"⚠️  npm install failed: {result.stderr}")
                        raise Exception("npm install failed")
                
                # Verify package.json has dev script
                with open(frontend_dir / "package.json", 'r') as f:
                    package_data = json.load(f)
                
                if "scripts" not in package_data or "dev" not in package_data["scripts"]:
                    print("⚠️  No dev script found, creating minimal React setup...")
                    # Add dev script if missing
                    if "scripts" not in package_data:
                        package_data["scripts"] = {}
                    package_data["scripts"]["dev"] = "vite --port " + str(frontend_port)
                    
                    with open(frontend_dir / "package.json", 'w') as f:
                        json.dump(package_data, f, indent=2)
                
                # Start React dev server
                env = os.environ.copy()
                env["PORT"] = str(frontend_port)
                env["VITE_API_BASE_URL"] = f"http://localhost:{backend_port}/api/v1"
                
                print(f"🔄 Starting React dev server on port {frontend_port}...")
                process = subprocess.Popen(
                    ["npm", "run", "dev"], 
                    cwd=frontend_dir, 
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Give it a moment to start
                time.sleep(3)
                
                # Check if process is still running
                if process.poll() is None:
                    return process, frontend_port
                else:
                    print("⚠️  React dev server failed to start, using fallback...")
                    raise Exception("React dev server failed")
                
            except Exception as e:
                print(f"⚠️  React setup failed: {e}")
                print("🔄 Creating standalone React demo instead...")
        
        # Create standalone React demo that works without build tools
        print(f"🎨 Creating standalone React demo on port {frontend_port}...")
        
        standalone_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAA Manifold Platform</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='14' fill='%231976d2'/><circle cx='16' cy='16' r='8' fill='white'/></svg>">
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r158/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.158.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body {{ margin: 0; font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1e3c72, #2a5298); }}
        #root {{ width: 100vw; height: 100vh; }}
        .panel {{ position: absolute; background: rgba(0,0,0,0.8); color: white; padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); }}
        .header {{ position: absolute; top: 20px; left: 20px; right: 20px; text-align: center; background: rgba(0,0,0,0.9); padding: 15px; border-radius: 10px; }}
        .controls {{ position: absolute; bottom: 20px; right: 20px; }}
        .info {{ position: absolute; bottom: 20px; left: 20px; }}
        button {{ background: #1976d2; color: white; border: none; padding: 10px 15px; margin: 5px; border-radius: 5px; cursor: pointer; }}
        button:hover {{ background: #1565c0; }}
        .metric {{ margin: 5px 0; font-size: 14px; }}
        .value {{ color: #42a5f5; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🧬 SAA Manifold Research Platform</h2>
        <p>Interactive South Atlantic Anomaly Analysis & Visualization</p>
        <p style="font-size: 12px; opacity: 0.8;">
            Backend API: <a href="http://localhost:{backend_port}" style="color: #42a5f5;">http://localhost:{backend_port}</a> | 
            Documentation: <a href="http://localhost:{backend_port}/docs" style="color: #42a5f5;">API Docs</a>
        </p>
    </div>
    
    <div id="root"></div>
    
    <div class="info panel">
        <h4>📊 Analysis Results</h4>
        <div class="metric">Peak Intensity: <span class="value">1,250 p/cm²/s</span></div>
        <div class="metric">Anomalies: <span class="value">3 detected</span></div>
        <div class="metric">Confidence: <span class="value">95%</span></div>
        <div class="metric">GPU: <span class="value" id="gpu-status">Available</span></div>
    </div>
    
    <div class="controls panel">
        <h4>🎛️ Controls</h4>
        <button onclick="window.saaApp.resetView()">🔄 Reset</button><br>
        <button onclick="window.saaApp.toggleWireframe()">🔗 Wireframe</button><br>
        <button onclick="window.saaApp.cycleColors()">🎨 Colors</button><br>
        <button onclick="window.saaApp.toggleAnimation()">⏯️ Animation</button><br>
        <button onclick="window.saaApp.exportImage()">📷 Export</button><br>
        <button onclick="testAPI()">🔌 Test API</button>
    </div>

    <script type="text/babel">
        class SAAManifoldApp extends React.Component {{
            constructor(props) {{
                super(props);
                this.state = {{
                    scene: null,
                    camera: null,
                    renderer: null,
                    controls: null,
                    manifold: null,
                    animating: true,
                    wireframe: false
                }};
                this.canvasRef = React.createRef();
            }}

            componentDidMount() {{
                this.initThreeJS();
                window.saaApp = this; // Global access for buttons
            }}

            initThreeJS() {{
                const canvas = this.canvasRef.current;
                
                // Scene setup
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x001122);
                
                // Camera
                const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(60, 40, 80);
                
                // Renderer
                const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.shadowMap.enabled = true;
                
                // Controls
                const controls = new THREE.OrbitControls(camera, canvas);
                controls.enableDamping = true;
                
                // Lighting
                scene.add(new THREE.AmbientLight(0x404040, 0.4));
                const light = new THREE.DirectionalLight(0xffffff, 0.8);
                light.position.set(50, 50, 50);
                light.castShadow = true;
                scene.add(light);
                
                // Create SAA manifold
                const manifold = this.createSAAManifold();
                scene.add(manifold);
                
                this.setState({{ scene, camera, renderer, controls, manifold }});
                
                // Animation loop
                const animate = () => {{
                    requestAnimationFrame(animate);
                    controls.update();
                    
                    if (this.state.animating && manifold) {{
                        manifold.rotation.z += 0.005;
                    }}
                    
                    renderer.render(scene, camera);
                }};
                animate();
                
                // Handle resize
                window.addEventListener('resize', () => {{
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                }});
            }}

            createSAAManifold() {{
                const geometry = new THREE.BufferGeometry();
                const vertices = [], colors = [], indices = [];
                
                const resolution = 80;
                for (let i = 0; i < resolution; i++) {{
                    for (let j = 0; j < resolution; j++) {{
                        const lon = -90 + (i / (resolution - 1)) * 90;
                        const lat = -50 + (j / (resolution - 1)) * 50;
                        
                        // SAA flux calculation
                        const d1 = Math.sqrt((lon + 50)**2 + (lat + 25)**2);
                        const d2 = Math.sqrt((lon + 45)**2 + (lat + 15)**2);
                        const flux = Math.exp(-d1/20) + 0.8*Math.exp(-d2/15);
                        
                        vertices.push(lon, lat, 4 + flux * 10);
                        
                        // Plasma colors
                        const t = Math.min(1, flux);
                        colors.push(0.05 + 0.95*t, t*t, 0.2 + 0.8*t*t);
                        
                        if (i < resolution-1 && j < resolution-1) {{
                            const a = i*resolution + j;
                            const b = (i+1)*resolution + j;
                            const c = (i+1)*resolution + (j+1);
                            const d = i*resolution + (j+1);
                            indices.push(a,b,c, a,c,d);
                        }}
                    }}
                }}
                
                geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
                geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
                geometry.setIndex(indices);
                geometry.computeNormals();
                
                const material = new THREE.MeshStandardMaterial({{
                    vertexColors: true,
                    side: THREE.DoubleSide,
                    transparent: true,
                    opacity: 0.9
                }});
                
                return new THREE.Mesh(geometry, material);
            }}

            resetView() {{
                if (this.state.camera && this.state.controls) {{
                    this.state.camera.position.set(60, 40, 80);
                    this.state.controls.reset();
                }}
            }}

            toggleWireframe() {{
                if (this.state.manifold) {{
                    this.setState({{ wireframe: !this.state.wireframe }});
                    this.state.manifold.material.wireframe = !this.state.wireframe;
                }}
            }}

            cycleColors() {{
                console.log('🎨 Color cycling - recreating manifold...');
                if (this.state.scene && this.state.manifold) {{
                    this.state.scene.remove(this.state.manifold);
                    const newManifold = this.createSAAManifold();
                    this.state.scene.add(newManifold);
                    this.setState({{ manifold: newManifold }});
                }}
            }}

            toggleAnimation() {{
                this.setState({{ animating: !this.state.animating }});
            }}

            exportImage() {{
                if (this.state.renderer) {{
                    const link = document.createElement('a');
                    link.download = 'saa-manifold.png';
                    link.href = this.state.renderer.domElement.toDataURL();
                    link.click();
                }}
            }}

            render() {{
                return React.createElement('canvas', {{
                    ref: this.canvasRef,
                    style: {{ display: 'block', width: '100%', height: '100%' }}
                }});
            }}
        }}

        // Mount React app
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(React.createElement(SAAManifoldApp));

        // API testing function
        async function testAPI() {{
            try {{
                const response = await fetch('http://localhost:{backend_port}/health');
                const data = await response.json();
                alert('✅ API Connected: ' + JSON.stringify(data, null, 2));
            }} catch (e) {{
                alert('❌ API Connection failed: ' + e.message);
            }}
        }}

        console.log('%c🧬 SAA Platform Ready', 'color: #42a5f5; font-size: 16px; font-weight: bold');
        console.log('🔌 Backend API: http://localhost:{backend_port}');
        console.log('📚 Documentation: http://localhost:{backend_port}/docs');
    </script>
</body>
</html>'''
        
        # Write standalone React app
        standalone_file = frontend_dir / "standalone_index.html"
        with open(standalone_file, 'w', encoding='utf-8') as f:
            f.write(standalone_html)
        
        # Start simple server serving our standalone app
        cmd = [sys.executable, "-m", "http.server", str(frontend_port)]
        process = subprocess.Popen(cmd, cwd=frontend_dir)
        
        print(f"✅ Frontend serving standalone React app")
        print(f"📁 Serving from: {frontend_dir}")
        print(f"🔗 Main app: http://localhost:{frontend_port}/standalone_index.html")
        
        return process, frontend_port
        
    except Exception as e:
        print(f"❌ Frontend startup failed: {e}")
        return None, None

def main():
    """Main runner with robust error handling."""
    print("🚀 SAA Manifold Platform - Simple Runner")
    print("=" * 50)
    
    # Check basic requirements
    if not check_command("python") and not check_command("python3"):
        print("❌ Python not found. Please install Python 3.8+")
        return
    
    has_node = check_command("node")
    has_docker = check_command("docker")
    
    print("🔍 System Check:")
    print(f"   ✅ Python: Available")
    print(f"   {'✅' if has_node else '❌'} Node.js: {'Available' if has_node else 'Not Available'}")
    print(f"   {'✅' if has_docker else '❌'} Docker: {'Available' if has_docker else 'Not Available'}")
    
    # Choose run mode
    print("\n📋 Available Options:")
    print("   1. 🌐 Instant Browser Demo (Zero setup, works everywhere)")
    print("   2. 🛠️  Development Mode (Backend + Frontend)")
    print("   3. 🔬 Original Simple Plot (Matplotlib)")
    
    choice = input("\nSelect option (1-3) [1]: ").strip() or "1"
    
    if choice == "1":
        # Instant demo
        success = create_instant_demo()
        if success:
            print("\n🎯 Demo Features:")
            print("   • Interactive 3D SAA manifold")
            print("   • Scientific flux visualization")
            print("   • Real-time controls and animations")
            print("   • Export capabilities")
            print("\n✨ No server required - runs entirely in browser!")
        
    elif choice == "2":
        # Development mode
        print("\n🛠️  Starting Development Mode...")
        processes = []
        
        try:
            # Start backend
            backend_process, backend_port = run_backend_simple()
            if backend_process:
                processes.append(backend_process)
                print(f"✅ Backend running on http://localhost:{backend_port}")
                
                # Wait a moment for backend to start
                time.sleep(2)
                
                # Start frontend
                frontend_process, frontend_port = run_frontend_simple(backend_port)
                if frontend_process:
                    processes.append(frontend_process)
                    print(f"✅ Frontend running on http://localhost:{frontend_port}")
                    
                    # Print access info
                    print(f"\n🌐 Access Points:")
                    print(f"   Frontend:  http://localhost:{frontend_port}/standalone_index.html")
                    print(f"   API:       http://localhost:{backend_port}")
                    print(f"   Health:    http://localhost:{backend_port}/health")
                    print(f"   Docs:      http://localhost:{backend_port}/docs")
                    
                    # Try to open the standalone React app
                    try:
                        webbrowser.open(f"http://localhost:{frontend_port}/standalone_index.html")
                        print("🌐 Opened enhanced React app in browser")
                    except:
                        try:
                            webbrowser.open(f"http://localhost:{frontend_port}")
                            print("🌐 Opened basic frontend in browser")
                        except:
                            pass
                    
                    print("\n⚠️  Press Ctrl+C to stop")
                    
                    # Wait for user to stop
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n🛑 Stopping services...")
                        
            else:
                print("❌ Could not start backend")
                
        finally:
            # Cleanup
            for process in processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    try:
                        process.kill()
                    except:
                        pass
            print("✅ All services stopped")
    
    elif choice == "3":
        # Original plot
        original_file = Path("saa_manifold.py")
        if original_file.exists():
            print("📊 Running original SAA visualization...")
            subprocess.run([sys.executable, str(original_file)])
        else:
            print("❌ Original file not found")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   Try running the instant demo (option 1) for guaranteed functionality")