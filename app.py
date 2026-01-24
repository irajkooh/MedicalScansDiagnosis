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

def analyze_medical_image(image, question, history, progress=gr.Progress()):
    """Analyze medical image with custom question and conversation history"""
    if image is None:
        return "Please upload an image first.", history, ""
    
    start_time = time.time()
    
    progress(0.1, desc="🔍 Step 1/10: Starting analysis...")
    
    progress(0.2, desc="📷 Step 2/10: Loading medical image...")
    
    # Create messages with conversation history
    progress(0.3, desc="📝 Step 3/10: Preparing prompt...")
    messages = []
    
    # Add conversation history
    for prev_q, prev_a in history:
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": prev_q}]
        })
        messages.append({
            "role": "assistant",
            "content": [{"type": "text", "text": prev_a}]
        })
    
    # Add current question with image
    messages.append({
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": question}
        ]
    })
    
    progress(0.4, desc="🤖 Step 4/10: Initializing AI model...")
    
    progress(0.5, desc="🧠 Step 5/10: Processing with MedGemma AI...")
    
    # Run inference
    try:
        output = pipe(text=messages, max_new_tokens=500)
        
        progress(0.6, desc="🔬 Step 6/10: Analyzing results...")
        progress(0.7, desc="📊 Step 7/10: Extracting findings...")
        result = output[0]["generated_text"][-1]["content"]
        
        progress(0.8, desc="📋 Step 8/10: Formatting output...")
        progress(0.9, desc="✨ Step 9/10: Finalizing report...")
        
        # Calculate total time
        total_time = time.time() - start_time
        
        progress(1.0, desc=f"✅ Step 10/10: Complete! ({total_time:.1f}s)")
        
        # Update history
        new_history = history + [[question, result]]
        
        # Build full output with all conversations
        full_output = ""
        for i, (q, a) in enumerate(new_history, 1):
            full_output += f"Conversation {i}:\n\nQuestion: {q}\n\nAnswer: {a}\n\n{'='*80}\n\n"
        
        # Add total processing time at the end - make it prominent
        full_output += f"\n{'='*80}\n⏱️  TOTAL PROCESSING TIME: {total_time:.1f} seconds\n{'='*80}"
        
        # Format for copy: all conversations
        copy_text = full_output.strip()
        
        return full_output.strip(), new_history, copy_text
    except Exception as e:
        total_time = time.time() - start_time
        progress(1.0, desc=f"❌ Error occurred ({total_time:.1f}s)")
        error_msg = f"Error during analysis: {str(e)}"
        return error_msg, history, f"Question: {question}\n\nAnswer: {error_msg}"

def clear_history():
    """Clear conversation history, image, and output"""
    return None, "", [], ""

# Create Gradio interface with Blocks for custom copy button
with gr.Blocks(title="🏥 MedGemma 1.5: Medical Image Analysis") as demo:
    gr.Markdown("# 🏥 MedGemma 1.5: Medical Image Analysis")
    gr.Markdown("""
    Upload a medical image (X-ray, CT, MRI) and ask questions about it.
    
    **Supported imaging types:**
    - 2D: Chest X-rays, Brain X-rays, Dermatology, Histopathology
    - 3D: CT scans, MRI scans (volumetric data)
    
    ⚠️ **Important:** This is for research purposes only. Not for clinical diagnosis.
    """)
    
    # Hidden state for conversation history
    history_state = gr.State([])
    copy_state = gr.State("")
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Upload Medical Image")
            question_input = gr.Textbox(
                label="Ask a Question",
                placeholder="e.g., Describe this chest X-ray. What do you see?",
                value="Describe this medical image. What do you see?",
                lines=3
            )
            with gr.Row():
                submit_btn = gr.Button("Analyze", variant="primary")
                clear_btn = gr.Button("🗑️ Clear History", variant="secondary")
        
        with gr.Column():
            output_text = gr.Textbox(label="Analysis Result", lines=15)
            copy_btn = gr.Button("📋 Copy Results", size="sm")
    
    # Examples section
    gr.Examples(
        examples=[
            [None, "Describe this medical image. What do you see?"],
            [None, "Is this a normal or abnormal scan?"],
            [None, "What are the biological reasons for this abnormality?"],
            [None, "Provide detailed explanations for your diagnosis."],
            [None, "Summarize the findings in a concise manner."],
            [None, "What anatomical structures are visible in this image?"],
            [None, "Describe any pathological findings in this scan."],
            [None, "What is the overall quality of this medical image?"],
            [None, "Are there any signs of pneumonia, cardiomegaly, or pleural effusion?"],
            [None, "Identify and describe the location of the heart, lungs, and any abnormalities."],
        ],
        inputs=[image_input, question_input],
        cache_examples=False
    )
    
    # Connect the analyze button
    submit_btn.click(
        fn=analyze_medical_image,
        inputs=[image_input, question_input, history_state],
        outputs=[output_text, history_state, copy_state],
        show_progress="full",
        concurrency_limit=10
    )
    
    # Clear button functionality
    clear_btn.click(
        fn=clear_history,
        inputs=[],
        outputs=[image_input, output_text, history_state, copy_state]
    )
    
    # Copy button functionality (copies question + answer to clipboard via JavaScript)
    copy_btn.click(None, copy_state, None, js="(x) => {navigator.clipboard.writeText(x); return x;}")

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=10)
    demo.launch()
