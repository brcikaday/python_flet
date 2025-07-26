# 🗣️ SpeechEaseApp (Beta)

SpeechEaseApp is a simple, Python-based text-to-speech application built using the [Flet](https://flet.dev) framework.
It allows users to upload text or documents and listen to them read aloud — similar to popular apps like Speechify. It is designed to improve accessibility and aid users with ADHD, dyslexia, or visual impairments.

---

## 🚀 Features

- 📄 Upload and read text from files (PDF and DOCX supported)
- 🔊 Convert typed or uploaded text to speech
- 🖥️ Clean and interactive GUI with Flet
- ⛓️ Multi-threaded speech processing for smooth performance
- 🧠 Designed with accessibility and learning support in mind
- Supports reading or skipping text from image-embedded documents — a feature usually locked behind a paywall in apps like Speechify

---

## ❓ Why Use SpeechEaseApp?

Unlike many commercial alternatives like **Speechify**, SpeechEaseApp provides advanced reading features such as:
- ✅ **Free support for image-rich documents**
- ✅ **No subscription required**
- ✅ **Completely open-source and customizable**

---

## 🧪 Beta Notice

This is a Beta version of SpeechEaseApp. While it's under active development, key features like multi-format reading and basic speech controls are already functional — including the ability to handle image-embedded documents without any payment.

---


---

## 🛠 Tech Stack

- Language: Python
- Framework: [Flet](https://flet.dev)
- Libraries: 
  - `pyttsx3` (or similar for speech synthesis)
  - `pypdf` for reading PDF files
  - `python-docx` for reading Word documents
  - `threading` for background processing
- Platform: Desktop (runs locally)

---

## ⚙️ Installation

1. Clone the repository

```bash
git clone https://github.com/brcikaday/python_flet.git
cd python_flet/SpeechEaseApp
