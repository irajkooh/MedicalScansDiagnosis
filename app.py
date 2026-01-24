# use deployed app.py on HF space "Medical_Scans_Diagnosis"
# https://huggingface.co/spaces/irajkoohi/MedicalScansDiagnosis?logs=build


import gradio as gr
from transformers import pipeline
import torch
from PIL import Image
from pathlib import Path
from huggingface_hub import snapshot_download
import os
import time

# Get HF token from environment
hf_token = os.environ.get("MedicalScans_token")

if not hf_token:
    raise ValueError(
        "MedicalScans_token environment variable not found!\n"
        "Please add your Hugging Face token as a secret in Space settings:\n"
        "1. Go to Settings tab\n"
        "2. Navigate to 'Variables and secrets'\n"
        "3. Add MedicalScans_token with your token value from https://huggingface.co/settings/tokens"
    )

print(f"✓ MedicalScans_token found (length: {len(hf_token)})")

# Load model function
def load_model():
    model_dir = Path("./models/medgemma-1.5-4b-it")
    
    # Check if model exists locally
    model_exists = (
        model_dir.exists() 
        and any(model_dir.glob("*.safetensors")) 
        and (model_dir / "tokenizer_config.json").exists()
    )
    
    if model_exists:
        model_path = str(model_dir)
        print(f"Loading model from {model_path}")
    else:
        print("Downloading model from Hugging Face Hub...")
        model_dir.parent.mkdir(exist_ok=True)
        model_path = snapshot_download(
            repo_id="google/medgemma-1.5-4b-it",
            local_dir=str(model_dir),
            local_dir_use_symlinks=False,
            token=hf_token,
        )
        print(f"Model downloaded to {model_path}")
    
    # Load pipeline
    print("Loading pipeline...")
    pipe = pipeline(
        "image-text-to-text",
        model=model_path,
        dtype=torch.bfloat16,
        device="cuda" if torch.cuda.is_available() else "cpu",
        token=hf_token,
    )
    print(f"Model loaded successfully on {pipe.device}")
    
    return pipe

# Load model on startup
print("Initializing model...")
pipe = load_model()

def analyze_medical_image(image, question, progress=gr.Progress()):
    """Analyze medical image with custom question"""
    if image is None:
        return "Please upload an image first."
    
    progress(0, desc="🔍 Preparing image...")
    time.sleep(0.1)  # Brief pause to show progress
    
    # Create messages
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": question}
            ]
        }
    ]
    
    progress(0.3, desc="🧠 Analyzing with MedGemma AI...")
    
    # Run inference (fixed max_tokens)
    output = pipe(text=messages, max_new_tokens=500)
    
    progress(1.0, desc="✅ Complete!")
    
    return output[0]["generated_text"][-1]["content"]

# Create Gradio interface using simpler Interface API
demo = gr.Interface(
    fn=analyze_medical_image,
    inputs=[
        gr.Image(type="pil", label="Upload Medical Image"),
        gr.Textbox(
            label="Ask a Question",
            placeholder="e.g., Describe this chest X-ray. What do you see?",
            value="Describe this medical image. What do you see?",
            lines=3
        )
    ],
    outputs=gr.Textbox(label="Analysis Result", lines=15, show_copy_button=True),
    title="🏥 MedGemma 1.5: Medical Image Analysis",
    description="""
    Upload a medical image (X-ray, CT, MRI) and ask questions about it.
    
    **Supported imaging types:**
    - 2D: Chest X-rays, Brain X-rays, Dermatology, Histopathology
    - 3D: CT scans, MRI scans (volumetric data)
    
    ⚠️ **Important:** This is for research purposes only. Not for clinical diagnosis.
    """,
    examples=[
        [None, "Describe this chest X-ray. What do you see?"],
        [None, "Are there any signs of pneumonia, cardiomegaly, or pleural effusion?"],
        [None, "Identify and describe the location of the heart, lungs, and any abnormalities."],
        [None, "What is the overall quality of this medical image?"],
        [None, "Describe any pathological findings in this scan."],
        [None, "Is this a normal or abnormal scan?"],
        [None, "What anatomical structures are visible in this image?"]
    ],
    cache_examples=False
)

if __name__ == "__main__":
    demo.launch()
