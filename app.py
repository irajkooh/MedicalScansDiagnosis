# use deployed app.py on HF space "Chest_Scan_Diagnosis"
# https://huggingface.co/spaces/irajkoohi/ChestScanDiagnosis?logs=build


import gradio as gr
from transformers import pipeline
import torch
from PIL import Image
from pathlib import Path
from huggingface_hub import snapshot_download
import os

# Get HF token from environment
hf_token = os.environ.get("HF_TOKEN")

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

def analyze_medical_image(image, question, max_tokens=500):
    """Analyze medical image with custom question"""
    if image is None:
        return "Please upload an image first."
    
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
    
    # Run inference
    output = pipe(text=messages, max_new_tokens=max_tokens)
    return output[0]["generated_text"][-1]["content"]

# Create Gradio interface
with gr.Blocks(title="MedGemma 1.5 - Medical Image Analysis") as demo:
    gr.Markdown("""
    # 🏥 MedGemma 1.5: Medical Image Analysis
    
    Upload a medical image (X-ray, CT, MRI) and ask questions about it.
    
    **Supported imaging types:**
    - 2D: Chest X-rays, Brain X-rays, Dermatology, Histopathology
    - 3D: CT scans, MRI scans (volumetric data)
    
    ⚠️ **Important:** This is for research purposes only. Not for clinical diagnosis.
    """)
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Upload Medical Image")
            question_input = gr.Textbox(
                label="Ask a Question",
                placeholder="e.g., Describe this chest X-ray. What do you see?",
                value="Describe this medical image. What do you see?",
                lines=3
            )
            max_tokens = gr.Slider(
                minimum=100,
                maximum=1000,
                value=500,
                step=50,
                label="Max Response Length"
            )
            analyze_btn = gr.Button("🔍 Analyze Image", variant="primary")
        
        with gr.Column():
            output = gr.Textbox(label="Analysis Result", lines=15)
    
    # Example questions
    gr.Markdown("""
    **Example questions:**
    - Describe this chest X-ray. What do you see?
    - Are there any signs of pneumonia, cardiomegaly, or pleural effusion?
    - Identify and describe the location of the heart, lungs, and any abnormalities.
    - What is the overall quality of this medical image?
    - Describe any pathological findings in this scan.
    """)
    
    analyze_btn.click(
        fn=analyze_medical_image,
        inputs=[image_input, question_input, max_tokens],
        outputs=output
    )
    
    gr.Markdown("""
    ---
    ### 📚 Resources
    - [Model on HuggingFace](https://huggingface.co/google/medgemma-1.5-4b-it)
    - [Research Blog](https://research.google/blog/next-generation-medical-image-interpretation-with-medgemma-15-and-medical-speech-to-text-with-medasr/)
    
    **Citation:**
    ```
    @article{sellergren2025medgemma,
      title={MedGemma Technical Report},
      author={Sellergren et al.},
      journal={arXiv preprint arXiv:2507.05201},
      year={2025}
    }
    ```
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
