# type: ignore  # Suppress Pylance type warnings for this file
"""
Shap-E Generator - Text to 3D Model
Generates 3D models from text descriptions
"""
import torch
from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.notebooks import decode_latent_mesh

class ShapEGenerator:
    def __init__(self):
        """Initialize Shap-E models for text-to-3D generation"""
        print("🔄 Loading Shap-E models...")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load models (official way - do not replace these with torch.load)
        self.xm = load_model('transmitter', device=self.device)
        self.model = load_model('text300M', device=self.device)
        self.diffusion = diffusion_from_config(load_config('diffusion'))
        
        print(f"✅ Shap-E loaded on {self.device}")

    def generate_3d_from_text(self, text_prompt, output_path="output", num_samples=1):
        """
        Generate 3D model from text description
        
        Args:
            text_prompt: Text description (e.g., "A comfortable, rustic coffee mug")
            output_path: Output file path (without extension)
            num_samples: Number of variations to generate
        
        Returns:
            list: Paths to generated .obj files
        """
        print(f"📝 Generating from prompt: '{text_prompt}'")
        
        # Generate latents from text
        latents = sample_latents(
            batch_size=num_samples,
            model=self.model,
            diffusion=self.diffusion,
            guidance_scale=15.0,
            model_kwargs=dict(texts=[text_prompt] * num_samples),
            progress=True,
            clip_denoised=True,
            use_fp16=True,
            use_karras=True,
            karras_steps=64,
            sigma_min=1e-3,
            sigma_max=160,
            s_churn=0,
        )

        print("💾 Saving 3D models...")
        
        generated_files = []
        
        # Save each generated model
        for i, latent in enumerate(latents):
            # Decode latent to mesh
            mesh = decode_latent_mesh(self.xm, latent).tri_mesh()
            
            # Save as OBJ (binary mode required for mesh library)
            obj_path = f"{output_path}_{i}.obj"
            with open(obj_path, 'wb') as f:
                mesh.write_obj(f)
            
            print(f"✅ Saved: {obj_path}")
            generated_files.append(obj_path)
        
        return generated_files


if __name__ == "__main__":
    # Initialize generator
    generator = ShapEGenerator()
    
    # Generate 3D models from text
    result_files = generator.generate_3d_from_text(
        text_prompt="A comfortable, rustic coffee mug with a handle",
        output_path="coffee_mug",
        num_samples=2  # Generate 2 variations
    )
    
    print("\n" + "="*60)
    print("🎉 Generation Complete!")
    print(f"Generated {len(result_files)} 3D models:")
    for file in result_files:
        print(f"  📁 {file}")
    print("="*60)
