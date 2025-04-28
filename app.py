from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer
import spacy
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# Load ML models (cache globally)
sbert = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
nlp_en = spacy.load("en_core_web_sm")
nlp_zh = spacy.load("zh_core_web_sm")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/align', methods=['POST'])
def align_subtitles():
    # Get files
    en_srt = request.files['en_srt'].read().decode('utf-8')
    zh_srt = request.files['zh_srt'].read().decode('utf-8')
    
    # Parse SRTs
    en_subs = parse_srt(en_srt)
    zh_subs = parse_srt(zh_srt)
    
    # Align with meaning preservation
    results = []
    for en_sub in en_subs:
        best_match = None
        highest_score = 0
        
        # Find best ZH match within time window
        for zh_sub in zh_subs:
            time_diff = abs(parse_time(en_sub['start']) - parse_time(zh_sub['start']))
            if time_diff <= timedelta(seconds=2):  # 2s tolerance
                score = get_match_score(en_sub['text'], zh_sub['text'])
                if score > highest_score:
                    best_match = zh_sub
                    highest_score = score
        
        # Build result
        if best_match and highest_score > 0.65:  # Confidence threshold
            results.append({
                'en_text': en_sub['text'],
                'zh_text': best_match['text'],
                'start': en_sub['start'],
                'end': en_sub['end'],
                'confidence': round(highest_score * 100, 1)
            })
    
    return render_template('result.html', results=results)

def get_match_score(en, zh):
    """Calculate semantic similarity score (0-1)"""
    # Embedding similarity
    emb_score = sbert.encode([en, zh])
    emb_score = cosine_similarity([emb_score[0]], [emb_score[1]]).item()
    
    # Entity matching
    en_ents = {e.text for e in nlp_en(en).ents}
    zh_ents = {e.text for e in nlp_zh(zh).ents}
    entity_score = 0.2 if en_ents and zh_ents and not en_ents.isdisjoint(zh_ents) else 0
    
    return min(emb_score + entity_score, 1.0)

def parse_time(time_str):
    """Convert SRT time to datetime"""
    return datetime.strptime(time_str.replace(',', '.'), "%H:%M:%S.%f")

def parse_srt(content):
    """Parse SRT into list of dicts"""
    subs = []
    blocks = content.strip().split('\n\n')
    
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            subs.append({
                'index': lines[0],
                'start': lines[1].split(' --> ')[0],
                'end': lines[1].split(' --> ')[1],
                'text': ' '.join(lines[2:])
            })
    
    return subs
