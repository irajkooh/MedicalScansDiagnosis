# use deployed app.py on HF space "Medical_Scans_Diagnosis"
# https://huggingface.co/spaces/irajkoohi/MedicalScansDiagnosis?logs=build

# If running locally (uses Ollama — run: ollama run llama3.2-vision):
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

# Free port 7860 on local startup (lsof not available in HF containers)
subprocess.run("lsof -ti:7860 | xargs kill -9 2>/dev/null || true", shell=True)

# Detect environment early — determines which backend to use
is_hf_space = os.environ.get("SPACE_ID") is not None
running_on = "HuggingFace Space" if is_hf_space else "Local"

# ── Backend setup ─────────────────────────────────────────────────────────────
if is_hf_space:
    # HF Space → Groq (fast cloud inference)
    from groq import Groq

    if not os.environ.get("GROQ_API_KEY"):
        raise ValueError(
            "GROQ_API_KEY secret not set in Space settings.\n"
            "Go to Settings → Variables and secrets → add GROQ_API_KEY."
        )
    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    GROQ_MODEL = "llama-3.2-90b-vision-preview"
    llm_label = f"Groq / {GROQ_MODEL}"
    print(f"✓ Backend: Groq ({GROQ_MODEL})")

else:
    # Local → Ollama (no API key needed)
    import ollama as _ollama
    OLLAMA_MODEL = "llama3.2-vision"
    llm_label = f"Ollama / {OLLAMA_MODEL}"
    print(f"✓ Backend: Ollama ({OLLAMA_MODEL})")

# ── Device detection ──────────────────────────────────────────────────────────
def get_device_info():
    if torch.cuda.is_available():
        return f"CUDA — {torch.cuda.get_device_name(0)}"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "MPS (Apple Silicon)"
    return "CPU"

device_name = get_device_info()
print(f"✓ Running on: {running_on}, Device: {device_name}, LLM: {llm_label}")

# ── Info bar (shown at top of UI) ─────────────────────────────────────────────
info_html = f"""
<div style="background:#eff6ff;border:1px solid #3b82f6;border-radius:8px;padding:10px 18px;
            color:#1d4ed8;font-size:14px;display:flex;gap:32px;flex-wrap:wrap;margin-bottom:4px;">
  <span>🖥️ <b>Running:</b> {running_on}</span>
  <span>⚡ <b>Device:</b> {device_name}</span>
  <span>🧠 <b>LLM:</b> {llm_label}</span>
</div>
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def image_to_base64(img: Image.Image) -> str:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def image_to_bytes(img: Image.Image) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ── Inference ─────────────────────────────────────────────────────────────────
def analyze_medical_image(image, question, history, progress=gr.Progress()):
    if image is None:
        return "Please upload an image first.", history, ""

    start_time = time.time()
    progress(0.2, desc="📷 Encoding image...")

    try:
        if is_hf_space:
            # Build Groq messages (prior turns text-only, current turn has image)
            messages = []
            for prev_q, prev_a in history:
                messages.append({"role": "user", "content": prev_q})
                messages.append({"role": "assistant", "content": prev_a})
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{image_to_base64(image)}"}},
                    {"type": "text", "text": question}
                ]
            })

            progress(0.5, desc="🧠 Sending to Groq AI...")
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=500
            )
            result = response.choices[0].message.content

        else:
            # Build Ollama messages
            messages = []
            for prev_q, prev_a in history:
                messages.append({"role": "user", "content": prev_q})
                messages.append({"role": "assistant", "content": prev_a})
            messages.append({
                "role": "user",
                "content": question,
                "images": [image_to_bytes(image)]
            })

            progress(0.5, desc="🧠 Sending to Ollama...")
            response = _ollama.chat(model=OLLAMA_MODEL, messages=messages)
            result = response["message"]["content"]

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
        progress(1.0, desc=f"❌ Error ({total_time:.1f}s)")
        error_msg = f"Error during analysis: {str(e)}"
        return error_msg, history, f"Question: {question}\n\nAnswer: {error_msg}"

def clear_history():
    return None, "", [], ""

# ── Sample questions ──────────────────────────────────────────────────────────
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

# ── Gradio UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(title="🏥 Medical Image Analysis") as demo:

    gr.Markdown("# 🏥 Medical Image Analysis")
    gr.HTML(info_html)
    gr.Markdown("""
    Upload a medical image (X-ray, CT, MRI) and ask questions about it.

    **Supported imaging types:**
    - 2D: Chest X-rays, Brain X-rays, Dermatology, Histopathology
    - 3D: CT scans, MRI scans (volumetric data)

    ⚠️ **Important:** This is for research purposes only. Not for clinical diagnosis.
    """)

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
                stop_btn = gr.Button("⏹ Stop", variant="stop")
                read_btn = gr.Button("🔊 Read", size="sm", interactive=False)

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
                clear_btn = gr.Button("🗑️ Clear History", variant="secondary", size="sm")
                copy_btn = gr.Button("📋 Copy Results", size="sm", interactive=False)

    with gr.Accordion("💡 Sample Questions — click to auto-analyze", open=True):
        sample_btn_rows = []
        for i in range(0, len(SAMPLE_QUESTIONS), 2):
            with gr.Row():
                for q in SAMPLE_QUESTIONS[i:i+2]:
                    btn = gr.Button(q, size="sm", elem_classes=["sample-btn"])
                    sample_btn_rows.append((btn, q))

    # --- Event wiring ---

    submit_event = submit_btn.click(
        fn=analyze_medical_image,
        inputs=[image_input, question_input, history_state],
        outputs=[output_text, history_state, copy_state],
        show_progress="full",
        concurrency_limit=10
    ).then(
        fn=lambda: [gr.update(interactive=True), gr.update(interactive=True)],
        outputs=[copy_btn, read_btn]
    )

    def update_analyze_button(image, question):
        return gr.update(interactive=image is not None and bool(question and question.strip()))

    question_input.change(fn=update_analyze_button, inputs=[image_input, question_input], outputs=submit_btn)
    image_input.change(fn=update_analyze_button, inputs=[image_input, question_input], outputs=submit_btn)

    clear_btn.click(
        fn=clear_history,
        inputs=[],
        outputs=[image_input, output_text, history_state, copy_state]
    ).then(
        fn=lambda: [gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)],
        outputs=[submit_btn, copy_btn, read_btn]
    )

    copy_btn.click(
        None, output_text, None,
        js="""
        (x) => {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(x);
            } else {
                const t = document.createElement('textarea');
                t.value = x; document.body.appendChild(t); t.select();
                document.execCommand('copy'); document.body.removeChild(t);
            }
        }
        """
    )

    read_btn.click(
        None, output_text, None,
        js="""
        (text) => {
            if (!window.speechSynthesis) return;
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
            } else if (text) {
                const parts = text.split('==========').map(s => s.trim()).filter(s => s.length > 0);
                const utterance = new SpeechSynthesisUtterance(parts[parts.length - 1] || text);
                window.speechSynthesis.speak(utterance);
            }
        }
        """
    )

    sample_events = []
    for btn, q in sample_btn_rows:
        ev = btn.click(
            fn=lambda question=q: question,
            inputs=[], outputs=[question_input], queue=False
        ).then(
            fn=analyze_medical_image,
            inputs=[image_input, question_input, history_state],
            outputs=[output_text, history_state, copy_state],
            show_progress="full", concurrency_limit=10
        ).then(
            fn=lambda: [gr.update(interactive=True), gr.update(interactive=True)],
            outputs=[copy_btn, read_btn]
        )
        sample_events.append(ev)

    # Stop button cancels all running analysis events
    stop_btn.click(fn=None, cancels=[submit_event, *sample_events])

demo.queue(default_concurrency_limit=10)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True, ssr_mode=False)
else:
    # HF Spaces entry point
    demo.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False)
