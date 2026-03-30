# use deployed app.py on HF space "Medical_Scans_Diagnosis"
# https://huggingface.co/spaces/irajkoohi/MedicalScansDiagnosis?logs=build

# If running locally:
"""
clear && lsof -ti:7860 | xargs kill -9 2>/dev/null; fg 2>/dev/null && sleep 0.5 && pkill -9 -f "python app.py" || true
source .venv/bin/activate && python app.py

App running on: http://localhost:7860
"""
import gradio as gr
import torch
from PIL import Image
from pathlib import Path
import os
import time
import base64
from io import BytesIO
import subprocess
from groq import Groq

# Free port 7860 on local startup (lsof not available in HF containers)
subprocess.run("lsof -ti:7860 | xargs kill -9 2>/dev/null || true", shell=True)

# Auto-load GROQ_API_KEY from file if not already set (local dev)
if not os.environ.get("GROQ_API_KEY"):
    groq_key_file = Path(__file__).parent / ".GROQ_API_KEY.txt"
    if groq_key_file.exists():
        for line in groq_key_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("gsk_"):
                os.environ["GROQ_API_KEY"] = line
                break

groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY environment variable not found!\n"
        "Please add your Groq API key as a secret in Space settings:\n"
        "1. Go to Settings tab\n"
        "2. Navigate to 'Variables and secrets'\n"
        "3. Add GROQ_API_KEY with your key from https://console.groq.com/keys"
    )

print(f"✓ GROQ_API_KEY found (length: {len(groq_api_key)})")

# Initialize Groq client and model
client = Groq(api_key=groq_api_key)
GROQ_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"

# Detect available device
def get_device_info():
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        return f"CUDA — {device_name}"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "MPS (Apple Silicon)"
    else:
        return "CPU"

# Environment info
is_hf_space = os.environ.get("SPACE_ID") is not None
running_on = "HuggingFace Space" if is_hf_space else "Local"
device_name = get_device_info()

print(f"✓ Running on: {running_on}, Device: {device_name}, Model: {GROQ_MODEL}")

info_html = f"""
<div style="background:#eff6ff;border:1px solid #3b82f6;border-radius:8px;padding:10px 18px;
            color:#1d4ed8;font-size:14px;display:flex;gap:32px;flex-wrap:wrap;margin-bottom:4px;">
  <span>🖥️ <b>Running:</b> {running_on}</span>
  <span>⚡ <b>Device:</b> {device_name}</span>
  <span>🧠 <b>LLM:</b> Groq / {GROQ_MODEL}</span>
</div>
"""

def image_to_base64(img: Image.Image) -> str:
    """Convert PIL image to base64 PNG string."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def analyze_medical_image(image, question, history, progress=gr.Progress()):
    """Analyze medical image with custom question and conversation history"""
    if image is None:
        return "Please upload an image first.", history, ""

    start_time = time.time()

    progress(0.2, desc="📷 Encoding image...")

    img_b64 = image_to_base64(image)

    progress(0.4, desc="🧠 Sending to Groq AI...")

    # Build messages: prior turns are text-only, current turn includes image
    messages = []
    for prev_q, prev_a in history:
        messages.append({"role": "user", "content": prev_q})
        messages.append({"role": "assistant", "content": prev_a})

    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"}
            },
            {
                "type": "text",
                "text": question
            }
        ]
    })

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=500
        )

        progress(0.9, desc="📋 Formatting output...")

        result = response.choices[0].message.content
        total_time = time.time() - start_time

        progress(1.0, desc=f"✅ Complete! ({total_time:.1f}s)")

        new_history = history + [[question, result]]

        full_output = ""
        for q, a in new_history:
            full_output += f"Question: {q}\n\nAnswer: {a}\n\n{'='*10}\n\n"

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

# Create Gradio interface
with gr.Blocks(title="🏥 Medical Image Analysis — Groq AI") as demo:

    gr.Markdown("# 🏥 Medical Image Analysis — Powered by Groq AI")

    # Info bar shown at top of UI
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
