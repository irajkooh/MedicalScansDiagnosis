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
import threading

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
    estimated_total_time = 60  # Estimate 60 seconds for full process (CPU inference is slow)
    
    # Shared variables for threading
    result_container = {"output": None, "error": None, "done": False}
    
    # Create messages with conversation history
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
    
    # Run inference in a separate thread
    def run_inference():
        try:
            output = pipe(text=messages, max_new_tokens=500)
            result_container["output"] = output[0]["generated_text"][-1]["content"]
        except Exception as e:
            result_container["error"] = str(e)
        finally:
            result_container["done"] = True
    
    # Start inference thread
    inference_thread = threading.Thread(target=run_inference)
    inference_thread.start()
    
    # Update progress linearly based on time
    step_names = [
        "🔍 Starting analysis",
        "📷 Loading medical image",
        "📝 Preparing prompt",
        "🤖 Initializing AI model",
        "🧠 Processing with MedGemma AI",
        "🔬 Analyzing results",
        "📊 Extracting findings",
        "📋 Formatting output",
        "✨ Finalizing report",
        "✅ Complete!"
    ]
    
    # Update progress every 0.2 seconds for smoother animation
    # Dynamic total time estimation that adjusts as processing continues
    while not result_container["done"]:
        elapsed = time.time() - start_time
        
        # Dynamically estimate total time based on elapsed time
        # Assume we're always between 50-90% done to keep extending estimate
        if elapsed < estimated_total_time * 0.5:
            # Early phase: use initial estimate
            current_estimate = estimated_total_time
        else:
            # Later phase: assume we're 80% done, so total = elapsed / 0.8
            current_estimate = elapsed / 0.8
        
        # Linear progress relative to current estimate
        progress_pct = elapsed / current_estimate
        
        # Cap at 95% until actually done
        progress_pct = min(progress_pct, 0.95)
        
        step_index = int(progress_pct * 10)
        step_index = min(step_index, 9)  # Max step 10 (index 9)
        
        # Format time display with elapsed/current estimate
        desc = f"{step_names[step_index]} - {elapsed:.0f}/{current_estimate:.0f}s"
        progress(progress_pct, desc=desc)
        time.sleep(0.2)  # Update 5 times per second for smooth progress
    
    # Wait for thread to complete
    inference_thread.join()
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Final progress update with total time
    progress(1.0, desc=f"✅ Complete! - {total_time:.0f}/{total_time:.0f}s")
    
    # Handle results
    if result_container["error"]:
        error_msg = f"Error during analysis: {result_container['error']}"
        return error_msg, history, f"Question: {question}\n\nAnswer: {error_msg}"
    
    result = result_container["output"]
    
    # Update history
    new_history = history + [[question, result]]
    
    # Format conversation with number, question, and answer
    conversation_num = len(new_history)
    conversation_text = f"Conversation {conversation_num}:\n\nQuestion: {question}\n\nAnswer: {result}"
    
    # Build full output with all conversations
    full_output = ""
    for i, (q, a) in enumerate(new_history, 1):
        full_output += f"Conversation {i}:\n\nQuestion: {q}\n\nAnswer: {a}\n\n{'='*80}\n\n"
    
    # Format for copy: all conversations
    copy_text = full_output.strip()
    
    return full_output.strip(), new_history, copy_text

def clear_history():
    """Clear conversation history, image, and output"""
    return None, "", [], ""

# Custom CSS for green progress bar
custom_css = """
.progress-bar {
    background-color: #10b981 !important;
}
.progress-container progress::-webkit-progress-value {
    background-color: #10b981 !important;
}
.progress-container progress::-moz-progress-bar {
    background-color: #10b981 !important;
}
"""

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
    demo.launch(css=custom_css)
