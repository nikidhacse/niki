__all__ = ["BlenderScriptGenerator"]
import json, random, os

class BlenderScriptGenerator:
    """
    Loads a JSONL dataset of Blender Python scripting examples
    and returns random prompt/script pairs.
    This implementation searches common filenames in the same directory as the module.
    """
    CANDIDATES = [
        "blender_scripting_10k.jsonl",
        "blender_basic_1k.jsonl",
        "blender.jsonl",
        "blender_dataset.jsonl",
        "data/blender_scripting_10k.jsonl",
        "data/blender_basic_1k.jsonl"
    ]

    def __init__(self, dataset_path=None):
        # Resolve dataset path: explicit first, then search candidates relative to this file and cwd
        self.data = []
        if dataset_path:
            dataset_path = os.path.expanduser(dataset_path)
            if os.path.isabs(dataset_path) and os.path.exists(dataset_path):
                self.dataset_path = dataset_path
            else:
                # try relative to this file
                base = os.path.dirname(os.path.abspath(__file__))
                candidate = os.path.join(base, dataset_path)
                if os.path.exists(candidate):
                    self.dataset_path = candidate
                else:
                    self.dataset_path = dataset_path  # keep as-is, will fail later
        else:
            # search candidates
            base = os.path.dirname(os.path.abspath(__file__))
            found = None
            for name in self.CANDIDATES:
                paths = [os.path.join(base, name), os.path.join(os.getcwd(), name)]
                for p in paths:
                    if os.path.exists(p):
                        found = p
                        break
                if found:
                    break
            self.dataset_path = found

        self._load_dataset()

    def _load_dataset(self):
        if not self.dataset_path or not os.path.exists(self.dataset_path):
            print(f"[ERROR] Dataset file not found: {self.dataset_path}")
            return
        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        self.data.append(json.loads(line))
                    except json.JSONDecodeError:
                        # skip malformed lines but continue
                        continue
        except Exception as e:
            print(f"[ERROR] Failed to load dataset: {e}")

    def get_random_script(self):
        """Return only the script (completion) portion from a random dataset entry."""
        if not self.data:
            return "[ERROR] No scripts loaded."
        entry = random.choice(self.data)
        return entry.get("completion") or entry.get("script") or ""

    def get_prompt_and_script(self):
        """Return full entry: both prompt and script."""
        if not self.data:
            return {"prompt": "[ERROR] No data loaded.", "completion": ""}
        entry = random.choice(self.data)
        # normalize keys
        prompt = entry.get("prompt") or entry.get("instruction") or entry.get("text") or ""
        completion = entry.get("completion") or entry.get("script") or entry.get("text") or ""
        return {"prompt": prompt, "completion": completion}

if __name__ == "__main__":
    gen = BlenderScriptGenerator()
    s = gen.get_prompt_and_script()
    print("Prompt:", s.get("prompt"))
    print("\nScript:\n", s.get("completion"))

