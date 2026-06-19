# Plagiarism-Detection-System
An NLP-based plagiarism detection system built using Flask, incorporating TF-IDF vectorization, cosine similarity for comparison, sentence-level matching, and n-gram analysis.

---

## Features

- Upload and compare text/PDF files
- TF-IDF and Cosine Similarity based detection
- Sentence-Level Similarity Matching
- N-Gram Analysis
- Smart preprocessing using NLP
- Highlight matched words and sentences
- Side-by-side document preview
- PDF report export
- File statistics and plagiarism score display

---

## Tech Stack

### Backend
- Python
- Flask
- Scikit-learn
- PyPDF2
- ReportLab

### Frontend
- HTML
- CSS
- JavaScript

### NLP Techniques
- TF-IDF Vectorization
- Cosine Similarity
- Sentence Matching
- N-Gram Analysis
- Stop-word Removal

---

## Project Structure

```bash
Plagiarism-Detection-System/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js

```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yugantsinghchahar2003-crypto/Plagiarism-Detection-System
```

Move into the project folder:

```bash
cd Plagiarism-Detection-System
```

Create Virtual Environment:
```bash
python -m venv venv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

```bash
pip install flask scikit-learn nltk numpy pandas scipy joblib
```

```bash
pip install sentence-transformers torch
```

```bash
pip install PyPDF2
```

```bash
pip install reportlab


Run the application:


```bash
python app.py
```

Open in browser:

```text
http://127.0.0.1:5000
```

---

## Future Improvements

- Semantic similarity using BERT
- Multi-file comparison
- User authentication
- Database integration
- Cloud deployment

---

## Author

**Yugant Chahar**

GitHub:
https://github.com/yugantsinghchahar2003-crypto
