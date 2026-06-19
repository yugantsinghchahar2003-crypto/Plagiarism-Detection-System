from flask import Flask, render_template, request, jsonify, send_file
import PyPDF2
import re
from sklearn.feature_extraction.text import (
    TfidfVectorizer,
    ENGLISH_STOP_WORDS,
    CountVectorizer
)
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')

app = Flask(__name__)
last_result = {}

def read_file(file):
    try:
        if file.filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content + " "
            return text
        return file.read().decode("utf-8")
    except:
        return ""

def remove_questions(text):
    lines = text.split("\n")
    filtered = []
    for line in lines:
        line_lower = line.strip().lower()
        if "?" in line:
            continue
        if line_lower.startswith(
            ("what", "why", "how", "define", "explain")
        ):
            continue
        filtered.append(line)
    return "\n".join(filtered)

def split_sentences(text):
    sentences = re.split(r'[.!?]', text)
    cleaned = []
    for s in sentences:
        s = s.strip()
        if len(s.split()) > 4:
            cleaned.append(s)
    return cleaned

def get_meaningful_common_words(text1, text2):

    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    words1 = words1 - ENGLISH_STOP_WORDS
    words2 = words2 - ENGLISH_STOP_WORDS
    common = words1.intersection(words2)
    return list(common)

def get_semantic_score(text1, text2):
    e1 = model.encode(text1, convert_to_tensor=True)
    e2 = model.encode(text2, convert_to_tensor=True)
    return util.cos_sim(e1, e2).item() * 100

def sentence_similarity(sentences1, sentences2):
    matched = []
    all_sentences = sentences1 + sentences2
    if not all_sentences:
        return matched
    vectorizer = TfidfVectorizer(
        stop_words='english'
    )
    tfidf_matrix = vectorizer.fit_transform(all_sentences)
    vectors1 = tfidf_matrix[:len(sentences1)]
    vectors2 = tfidf_matrix[len(sentences1):]
    similarity_matrix = cosine_similarity(
        vectors1,
        vectors2
    )
    for i in range(len(sentences1)):
        for j in range(len(sentences2)):
            score = similarity_matrix[i][j]
            if score > 0.5:
                matched.append({
                    "sentence1": sentences1[i],
                    "sentence2": sentences2[j],
                    "score": round(score * 100, 2)
                })
    return matched

def document_similarity(text1, text2):

    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1,2)
    )
    vectors = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(
        vectors[0],
        vectors[1]
    )[0][0]
    return similarity * 100

def ngram_similarity(text1, text2):

    vectorizer = CountVectorizer(
        ngram_range=(2, 3),
        stop_words='english'
    )
    vectors = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(
        vectors[0],
        vectors[1]
    )[0][0]

    return similarity * 100
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/check", methods=["POST"])
def check():

    file1 = request.files["file1"]
    file2 = request.files["file2"]
    text1 = read_file(file1)
    text2 = read_file(file2)

    if not text1 or not text2:
        return jsonify({
            "error": "Invalid or corrupted file uploaded."
        })

    text1 = remove_questions(text1)
    text2 = remove_questions(text2)

    sentences1 = split_sentences(text1)
    sentences2 = split_sentences(text2)

    matched_sentences = sentence_similarity(
        sentences1,
        sentences2
    )
    semantic_score = get_semantic_score(text1, text2)

    total_sentences = max(len(sentences1), 1)

    if matched_sentences:
        total_score = sum(
            match["score"]
            for match in matched_sentences
        )
        sentence_score = total_score / total_sentences

    else:
        sentence_score = 0
    doc_score = document_similarity(
        text1,
        text2
    )
    ngram_score = ngram_similarity(
        text1,
        text2
    )
    common_words = get_meaningful_common_words(
        text1,
        text2
    )
    common_word_score = (
        len(common_words)
        / max(len(text1.split()), 1)
    ) * 100
    similarity = (
        (doc_score * 0.35)
        +
        (sentence_score * 0.25)
        +
        (ngram_score * 0.15)
        +
        (common_word_score * 0.05)
        +
        (semantic_score * 0.20)
    )
    status = "Original"

    if similarity > 70:
        status = "Highly Plagiarized"
    elif similarity > 50:
        status = "Plagiarized"
    elif similarity > 30:
        status = "Suspicious"
    else:
        status = "Original"

    global last_result

    last_result = {
        "similarity": round(similarity, 2),
        "status": status,
        "text1": text1[:50000],
        "text2": text2[:50000],
        "file1_name": file1.filename,
        "file2_name": file2.filename,
        "words1": len(text1.split()),
        "words2": len(text2.split()),
        "common_words": common_words[:1000],
        "matched_sentences": matched_sentences,
        "sentences1": len(sentences1),
        "sentences2": len(sentences2),
        "matched_count": len(matched_sentences),
        "paragraphs1": len(text1.split("\n\n")),
        "paragraphs2": len(text2.split("\n\n"))
    }

    return jsonify(last_result)

@app.route("/export")
def export():
    doc = SimpleDocTemplate("result.pdf")
    styles = getSampleStyleSheet()

    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 14
    styles['Normal'].leading = 22

    styles['Title'].fontName = 'Helvetica-Bold'
    styles['Title'].fontSize = 18
    styles['Title'].leading = 30

    content = [
        Paragraph(
            "<b>PlagDetect Report</b>",
            styles['Title']
        ),
        Paragraph(
            f"Plagiarism Score: {last_result['similarity']}%",
            styles['Normal']
        ),
        Paragraph(
            f"Status: {last_result['status']}",
            styles['Normal']
        ),
        Paragraph(
            f"File 1: {last_result['file1_name']}",
            styles['Normal']
        ),
        Paragraph(
            f"File 2: {last_result['file2_name']}",
            styles['Normal']
        ),
        Paragraph(
            f"File 1 Words: {last_result['words1']}",
            styles['Normal']
        ),
        Paragraph(
            f"File 2 Words: {last_result['words2']}",
            styles['Normal']
        ),
        Paragraph(
            f"Matched Sentences: {last_result['matched_count']}",
            styles['Normal']
        ),
        Paragraph(
            f"File 1 Sentences: {last_result['sentences1']}",
            styles['Normal']
        ),
        Paragraph(
            f"File 2 Sentences: {last_result['sentences2']}",
            styles['Normal']
        )
    ]
    doc.build(content)
    return send_file(
        "result.pdf",
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)