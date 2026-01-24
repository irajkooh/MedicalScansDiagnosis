# 🚀 Deploy MedGemma 1.5 to Hugging Face Spaces

This guide walks you through deploying the MedGemma 1.5 Medical Image Analysis application to Hugging Face Spaces.

## Prerequisites

- Hugging Face account ([Sign up here](https://huggingface.co/join))
- Git installed on your system
- Hugging Face token with read access ([Create token here](https://huggingface.co/settings/tokens))
- Access to the MedGemma model (see step 4)

---

## Step 1: Create a New Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in the details:
   - **Space name**: `MedicalScansDiagnosis`
   - **SDK**: Select **Gradio**
   - **Hardware**: Start with CPU (upgrade to GPU later for better performance)
   - **Visibility**: Choose Public or Private
3. Click "Create Space"
4. Note your Space URL: `https://huggingface.co/spaces/irajkoohi/MedicalScansDiagnosis`

---

## Step 2: Prepare Local Files

```bash
cd /Users/ik/UVcodes/MedicalScansDiagnosis

# Verify files exist
ls -la app.py requirements.txt README.md
```

---

## Step 3: Initialize Git and Push to Space

```bash
# Initialize git repository if not already done
git init

# Add the Space as a remote
git remote add space https://huggingface.co/spaces/irajkoohi/MedicalScansDiagnosis

# Stage files for commit
git add app.py requirements.txt README.md

# Commit files
git commit -m "Initial deployment of MedGemma 1.5 medical image analyzer"

# Push to Space (you'll be prompted for credentials)
git push space main
```

**Note**: When prompted for credentials:
- Username: Your Hugging Face username
- Password: Use your Hugging Face **token** (not your password)

---

## Step 4: Request Model Access

Before your Space can load the model, you need access:

1. Visit [google/medgemma-1.5-4b-it](https://huggingface.co/google/medgemma-1.5-4b-it)
2. Click **"Agree and access repository"**
3. Wait for approval (usually instant)

---

## Step 5: Add HF Token as Secret

Your Space needs your token to download the gated model:

1. Go to your Space page on Hugging Face
2. Click **"Settings"** tab
3. Navigate to **"Variables and secrets"**
4. Click **"New secret"**
5. Add the following:
   - **Name**: `MedicalScans_token`
   - **Value**: Your Hugging Face token (paste it here)
6. Click **"Save"**

---

## Step 6: Monitor Deployment

1. Go back to your Space's main page
2. Watch the "Building" logs in real-time
3. First build takes 5-10 minutes (installing dependencies)
4. Model download happens on first use (adds ~5 more minutes)

---

## Step 7: Upgrade Hardware (Optional but Recommended)

For better performance:

1. Go to Space **Settings** → **Hardware**
2. Select a GPU option:
   - **T4 small** (Free tier, limited hours)
   - **T4 medium** (Better performance)
   - **A10G small** (Fastest, paid)
3. Click **"Save"**
4. Space will restart with new hardware

---

## Troubleshooting

### Push Failed / Remote Already Exists
```bash
# Remove existing remote and re-add
git remote remove space
git remote add space https://huggingface.co/spaces/irajkoohi/MedicalScansDiagnosis
git push space main
```

### Authentication Failed
- Use your HF **token** as password, not your account password
- Generate a new token if needed: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Model Access Denied
- Ensure you've accepted the model agreement at [google/medgemma-1.5-4b-it](https://huggingface.co/google/medgemma-1.5-4b-it)
- Verify your `MedicalScans_token` secret is correctly set in Space settings
- Token must have **read** permissions

### Out of Memory Errors
- Upgrade to GPU hardware in Space settings
- Model requires ~8GB VRAM

### Build Fails
- Check logs in the Space page
- Verify `requirements.txt` is present
- Ensure all dependencies are compatible

---

## Files Created for Deployment

- **`app.py`**: Main Gradio application
- **`requirements.txt`**: Python dependencies
- **`README.md`**: Space documentation (displayed on Space page)

---

## Alternative: Manual Upload via Web UI

If you prefer not to use Git:

1. Go to your Space page
2. Click **"Files"** tab
3. Click **"Add file"** → **"Upload files"**
4. Upload: `app.py`, `requirements.txt`, `README.md`
5. Click **"Commit changes to main"**

---

## Testing Your Deployed Space

1. Once building completes, the Space will be live
2. Upload a test medical image (chest X-ray)
3. Try example questions like:
   - "Describe this chest X-ray. What do you see?"
   - "Are there any signs of pneumonia?"
4. Verify the model responds correctly

---

## Sharing Your Space

Once deployed, share your Space URL:
- **Direct link**: `https://huggingface.co/spaces/irajkoohi/MedicalScansDiagnosis`
- **Embed in website**: Use the embed code from Space settings

---

## Cost Considerations

- **CPU Spaces**: Free (persistent)
- **GPU Spaces**: 
  - T4 small: Limited free hours, then paid
  - Other GPUs: Paid per hour
- **Check pricing**: [huggingface.co/pricing](https://huggingface.co/pricing)

---

## Next Steps

- ⭐ Add example medical images to the Space
- 🎨 Customize the Gradio interface in `app.py`
- 📊 Add analytics to track usage
- 🔧 Fine-tune the model for specific medical domains
- 🌐 Share with the medical AI community

---

## Support

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Gradio Documentation](https://www.gradio.app/docs)
- [MedGemma Model Card](https://huggingface.co/google/medgemma-1.5-4b-it)

---

**Created**: January 24, 2026  
**Model**: MedGemma 1.5 (google/medgemma-1.5-4b-it)  
**Framework**: Gradio + Transformers  
**Space**: https://huggingface.co/spaces/irajkoohi/MedicalScansDiagnosis
