---
title: MedGemma 1.5 Medical Image Analysis
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.9.0
app_file: app.py
pinned: false
license: apache-2.0
python_version: 3.12
---

# MedGemma 1.5: Medical Image Analysis

This Space demonstrates Google's MedGemma 1.5, the first open-source multimodal AI model with 3D medical imaging capabilities.

## Features

- **2D Imaging Support**: Chest X-rays, Brain X-rays, Dermatology, Histopathology
- **3D Imaging Support**: CT scans, MRI scans (volumetric data)
- **Interactive Analysis**: Upload any medical image and ask custom questions

## How to Use

1. Upload a medical image (X-ray, CT, MRI scan)
2. Enter your question about the image
3. Click "Analyze Image" to get AI-powered insights

## Important Notes

⚠️ **This tool is for research and educational purposes only.**
- Outputs must be validated by medical professionals
- Not intended for clinical diagnosis
- Should not replace professional medical advice

## Performance Highlights

- CT classification: 61% accuracy
- MRI classification: 65% accuracy
- MedQA: 69% accuracy
- Fine-tuned version: 80% on imaging tasks

## Access Requirements

This model is gated. To use it:
1. Visit [google/medgemma-1.5-4b-it](https://huggingface.co/google/medgemma-1.5-4b-it)
2. Click "Agree and access repository"
3. Add your HF token as a Space secret named `HF_TOKEN`

## Resources

- [Model Card](https://huggingface.co/google/medgemma-1.5-4b-it)
- [Research Blog](https://research.google/blog/next-generation-medical-image-interpretation-with-medgemma-15-and-medical-speech-to-text-with-medasr/)
- [Official GitHub](https://github.com/Google-Health/medgemma)
