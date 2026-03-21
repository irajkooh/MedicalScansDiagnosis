# use deployed app.py on HF space "Medical_Scans_Diagnosis"
# https://huggingface.co/spaces/irajkoohi/MedicalScansDiagnosis?logs=build

# If running locally:
"""
clear && lsof -ti:7860 | xargs kill -9 2>/dev/null; fg 2>/dev/null && sleep 0.5 && pkill -9 -f "python app.py" || true
source .venv/bin/activate && GROQ_API_KEY=YOUR_HF_TOKEN_HERE python app.py

App running on: http://localhost:7860
"""
import gradio as gr
from transformers import pipeline
import torch
from PIL import Image
from pathlib import Path
from huggingface_hub import snapshot_download
import os
import time
import subprocess

# Clear screen and free port 7860 on local startup
os.system("clear")
subprocess.run("lsof -ti:7860 | xargs kill -9 2>/dev/null || true", shell=True)

# Auto-load HF_TOKEN from file if not already set (local dev)
if not os.environ.get("HF_TOKEN"):
    hf_token_file = Path(__file__).parent / ".HF_token.txt"
    if hf_token_file.exists():
        os.environ["HF_TOKEN"] = hf_token_file.read_text().strip()

# HF token for downloading gated model
hf_token = os.environ.get("HF_TOKEN")

if not hf_token:
    raise ValueError(
        "HF_TOKEN environment variable not found!\n"
        "Please add your Hugging Face token as a secret in Space settings:\n"
        "1. Go to Settings tab\n"
        "2. Navigate to 'Variables and secrets'\n"
        "3. Add HF_TOKEN with your token value from https://huggingface.co/settings/tokens"
    )

print(f"✓ HF_TOKEN found (length: {len(hf_token)})")

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
        device="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"),
        token=hf_token,
    )
    print(f"Model loaded successfully on {pipe.device}")

    return pipe

# Load model on startup
print("Initializing model...")
pipe = load_model()

# Environment info
is_hf_space = os.environ.get("SPACE_ID") is not None
running_on = "HuggingFace Space" if is_hf_space else "Local"
device_name = str(pipe.device)
model_name = "google/medgemma-1.5-4b-it"

info_html = f"""
<div style="background:#eff6ff;border:1px solid #3b82f6;border-radius:8px;padding:10px 18px;
            color:#1d4ed8;font-size:14px;display:flex;gap:32px;flex-wrap:wrap;margin-bottom:4px;">
  <span>🖥️ <b>Running:</b> {running_on}</span>
  <span>⚡ <b>Device:</b> {device_name}</span>
  <span>🧠 <b>LLM:</b> {model_name}</span>
</div>
"""

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
        result = output[0]["generated_text"][-1]["content"]  # type: ignore

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
            full_output += f"Conversation {i}:\n\nQuestion: {q}\n\nAnswer: {a}\n\n{'='*10}\n\n"

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

# Sample questions
SAMPLE_QUESTIONS = [
    "Describe this medical image. What do you see?",
    "Is this a normal or abnormal scan?",
    "What are the biological reasons for this abnormality?",
    "Provide detailed explanations for your diagnosis.",
    "Summarize the findings in a concise manner.",
    "What anatomical structures are visible in this image?",
    "Describe any pathological findings in this scan.",
    "What is the overall quality of this medical image?",
    "Are there any signs of pneumonia, cardiomegaly, or pleural effusion?",
    "Identify and describe the location of the heart, lungs, and any abnormalities.",
]

# Custom CSS
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
.sample-btn {
    text-align: left !important;
    font-size: 13px !important;
}
"""

# Create Gradio interface
with gr.Blocks(title="🏥 MedGemma 1.5: Medical Image Analysis", css=custom_css) as demo:

    gr.Markdown("# 🏥 MedGemma 1.5: Medical Image Analysis")

    # Info bar
    gr.HTML(info_html)
    gr.Markdown("""
    Upload a medical image (X-ray, CT, MRI) and ask questions about it.

    **Supported imaging types:**
    - 2D: Chest X-rays, Brain X-rays, Dermatology, Histopathology
    - 3D: CT scans, MRI scans (volumetric data)

    ⚠️ **Important:** This is for research purposes only. Not for clinical diagnosis.
    """)

    # Hidden state
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
                submit_btn = gr.Button("Analyze", variant="primary", interactive=False)
                clear_btn = gr.Button("🗑️ Clear History", variant="secondary")

        with gr.Column():
            output_text = gr.Textbox(
                label="Analysis Results",
                lines=24,
                autoscroll=True,
                show_label=True,
                container=True,
                interactive=False
            )
            with gr.Row():
                read_btn = gr.Button("🔊 Read", size="sm", interactive=False)
                copy_btn = gr.Button("📋 Copy Results", size="sm", interactive=False)

    # Sample questions section
    with gr.Accordion("💡 Sample Questions — click to auto-analyze", open=True):
        sample_btn_rows = []
        for i in range(0, len(SAMPLE_QUESTIONS), 2):
            with gr.Row():
                for q in SAMPLE_QUESTIONS[i:i+2]:
                    btn = gr.Button(q, size="sm", elem_classes=["sample-btn"])
                    sample_btn_rows.append((btn, q))

    # --- Event wiring ---

    # Analyze button
    submit_btn.click(
        fn=analyze_medical_image,
        inputs=[image_input, question_input, history_state],
        outputs=[output_text, history_state, copy_state],
        show_progress="full",
        concurrency_limit=10
    ).then(
        fn=lambda: [gr.update(interactive=True), gr.update(interactive=True)],
        outputs=[copy_btn, read_btn]
    )

    # Enable/disable Analyze button based on image + question
    def update_analyze_button(image, question):
        has_image = image is not None
        has_question = len(question.strip()) > 0 if question else False
        return gr.update(interactive=has_image and has_question)

    question_input.change(
        fn=update_analyze_button,
        inputs=[image_input, question_input],
        outputs=submit_btn
    )

    image_input.change(
        fn=update_analyze_button,
        inputs=[image_input, question_input],
        outputs=submit_btn
    )

    # Clear button
    clear_btn.click(
        fn=clear_history,
        inputs=[],
        outputs=[image_input, output_text, history_state, copy_state]
    ).then(
        fn=lambda: [gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)],
        outputs=[submit_btn, copy_btn, read_btn]
    )

    # Copy button (JS clipboard)
    copy_btn.click(
        None,
        output_text,
        None,
        js="""
        (x) => {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(x);
            } else {
                const textarea = document.createElement('textarea');
                textarea.value = x;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
            }
        }
        """
    )

    # Read button (Web Speech API toggle)
    read_btn.click(
        None,
        output_text,
        None,
        js="""
        (text) => {
            if (!window.speechSynthesis) return;
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
            } else if (text) {
                const parts = text.split('==========').map(s => s.trim()).filter(s => s.length > 0);
                const lastConversation = parts[parts.length - 1] || text;
                const utterance = new SpeechSynthesisUtterance(lastConversation);
                window.speechSynthesis.speak(utterance);
            }
        }
        """
    )

    # Sample question buttons — set question then auto-analyze
    for btn, q in sample_btn_rows:
        btn.click(
            fn=lambda question=q: question,
            inputs=[],
            outputs=[question_input],
            queue=False
        ).then(
            fn=analyze_medical_image,
            inputs=[image_input, question_input, history_state],
            outputs=[output_text, history_state, copy_state],
            show_progress="full",
            concurrency_limit=10
        ).then(
            fn=lambda: [gr.update(interactive=True), gr.update(interactive=True)],
            outputs=[copy_btn, read_btn]
        )

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=10)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        inbrowser=True
    )
