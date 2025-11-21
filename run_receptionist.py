import subprocess
import sys
import time
import requests

def wait_for_server(url, retries=30, delay=1):
    """Wait for Flask server to start"""
    print(f"Waiting for server to start at {url}...")
    
    for i in range(retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Server is UP! Model loaded: {data.get('model_loaded', False)}")
                return True
        except requests.exceptions.ConnectionError:
            if i % 5 == 0 and i > 0:
                print(f"  Still waiting... ({i}/{retries})")
        except Exception:
            pass
        time.sleep(delay)
    
    print("✗ Server failed to start")
    return False

def main():
    print("\n" + "="*70)
    print("  🤖 AI RECEPTIONIST - STARTUP SEQUENCE")
    print("="*70)
    
    # Start LLM server
    print("\n[1/2] Starting LLM server on port 8000...")
    llm_process = subprocess.Popen(
        [sys.executable, "llm_server.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    
    # Wait for Flask to start (fast now!)
    if not wait_for_server("http://localhost:8000/", retries=30, delay=1):
        print("\n✗ Failed to start LLM server")
        llm_process.terminate()
        return
    
    # Start chat UI
    print("\n[2/2] Starting chat web UI on port 5000...")
    chat_process = subprocess.Popen(
        [sys.executable, "chat_server.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    
    time.sleep(2)
    
    # Success!
    print("\n" + "="*70)
    print("  ✅ BOTH SERVERS ARE RUNNING!")
    print("="*70)
    print(f"\n  🌐 Open your browser to: http://localhost:5000")
    print(f"\n  ⚠️  IMPORTANT: Your FIRST message will take 1-2 minutes")
    print(f"     (Model loads on first use. After that, responses are faster)")
    print(f"\n  Press CTRL+C here to stop all servers")
    print("="*70 + "\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all servers...")
        llm_process.terminate()
        chat_process.terminate()
        print("✓ Shutdown complete\n")

if __name__ == "__main__":
    main()
