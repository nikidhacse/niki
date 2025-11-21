import os, subprocess, time

BLACKLIST = {
    "gradio_app.py",
    "shap_e_generator.py",
    "triposr_generator.py",  # removed
    "run.py",  # may import heavy deps like rembg/onnxruntime
    "train_llm.py"
}

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(base):
        if file.endswith(".py") and file not in ("run_everything.py",) and file not in BLACKLIST:
            path = os.path.join(base, file)
            print(f"[STARTING] {file}")
            subprocess.Popen(["python", path], shell=True)
            time.sleep(0.2)
    print("=== ALL MODULES STARTED ===")

if __name__ == '__main__':
    main()
