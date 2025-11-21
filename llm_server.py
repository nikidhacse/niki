import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
import logging
import torch
from typing import Optional

from core_engine import ReceptionistCore
from llm_manager import LLMManager
from small_model_response_generator import SmallLLMResponseGenerator
from interfaces import ResponseGenerator
from data_models import IntentResult
from api_gateway import APIGateway

# Blender script generator - robust path handling
try:
    from output_module import BlenderScriptGenerator
    BASE = os.path.dirname(os.path.abspath(__file__))
    # try common filenames
    candidates = [
        os.path.join(BASE, "blender_scripting_10k.jsonl"),
        os.path.join(BASE, "blender_basic_1k.jsonl"),
        os.path.join(BASE, "blender.jsonl"),
        os.path.join(BASE, "blender_dataset.jsonl"),
        os.path.join(BASE, "data", "blender_scripting_10k.jsonl"),
    ]
    script_path = None
    for c in candidates:
        if os.path.exists(c):
            script_path = c
            break
    # fallback to None (generator will search)
    script_gen = BlenderScriptGenerator(script_path) if script_path else BlenderScriptGenerator()
    logging.info("Blender script generator initialized.")
except Exception as e:
    script_gen = None
    logging.warning(f"Blender script generator not available: {e}")

app = Flask(__name__)

# Global variables
api_gateway: Optional[APIGateway] = None
system_initialized = False
initialization_lock = False

class LLMManagerAdapter(ResponseGenerator):
    def __init__(self, llm_manager: LLMManager, default_domain: str = "smollm3"):
        self.llm_manager = llm_manager
        self.default_domain = default_domain

    def initialize(self) -> bool:
        return True

    def generate(self, intent_result: IntentResult):
        domain = self.default_domain
        return self.llm_manager.generate_response(intent_result, domain)

    def cleanup(self) -> None:
        for gen in self.llm_manager.generators.values():
            gen.cleanup()

def create_system() -> APIGateway:
    logging.basicConfig(level=logging.INFO)
    print("\n" + "=" * 60)
    print("🔄 LOADING LLM MODEL (1-2 minutes)...")
    print("=" * 60)
    
    receptionist = ReceptionistCore()
    llm_manager = LLMManager()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    smollm_gen = SmallLLMResponseGenerator(device=device)
    llm_manager.register_generator("smollm3", smollm_gen)
    llm_manager.set_default_generator(smollm_gen)

    llm_adapter = LLMManagerAdapter(llm_manager)
    gateway = APIGateway()

    def llm_response_handler(text: str):
        # intercept blender requests
        triggers = ["blender", "bpy", "blender script", "generate a blender", "python for blender", "blender python"]
        lowered = text.lower() if isinstance(text, str) else ""
        if script_gen is not None and any(t in lowered for t in triggers):
            try:
                data = script_gen.get_prompt_and_script()
                return {
                    "text": f"Here is your Blender script (copy & paste into Blender):",
                    "blender_script": data.get("completion"),
                    "action": None,
                    "module": "blender_script",
                }
            except Exception as e:
                logging.error(f"Error generating blender script: {e}")
                # fall through to LLM response

        intent = IntentResult(raw_text=text, intent="", confidence=1.0, entities=[])
        response = llm_adapter.generate(intent)
        return {
            "text": response.text,
            "action": getattr(response, "action", None),
            "module": getattr(response, "module", None),
        }

    gateway.register_route("/llm_chat", llm_response_handler)
    
    print("=" * 60)
    print("✅ MODEL LOADED SUCCESSFULLY!")
    print("=" * 60 + "\n")
    
    return gateway

@app.route('/')
def health_check():
    return jsonify({
        "status": "ready", 
        "service": "LLM Server",
        "model_loaded": system_initialized
    }), 200

@app.route('/generate-script', methods=['GET'])
def generate_script_endpoint():
    if script_gen is None:
        return jsonify({"error": "Blender script generator not available"}), 500
    try:
        data = script_gen.get_prompt_and_script()
        return jsonify(data), 200
    except Exception as e:
        logging.error(f"Error serving /generate-script: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/llm_chat', methods=['POST'])
def llm_chat():
    global api_gateway, system_initialized, initialization_lock
    
    if not system_initialized:
        if initialization_lock:
            return jsonify({"error": "Model is currently loading, please wait..."}), 503
        
        initialization_lock = True
        try:
            api_gateway = create_system()
            system_initialized = True
        except Exception as e:
            initialization_lock = False
            logging.error(f"Failed to initialize system: {e}")
            return jsonify({"error": f"System initialization failed: {str(e)}"}), 500
        finally:
            initialization_lock = False
    
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data["text"]
    
    try:
        if api_gateway is None:
            return jsonify({"error": "System not initialized"}), 500
            
        result = api_gateway.handle_route("/llm_chat", text=text)
        # ensure blender_script key is included if present
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in llm_chat: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 STARTING FLASK SERVER ON PORT 8000...")
    print("⚠️  Model will load on FIRST chat request (1-2 min wait)")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
