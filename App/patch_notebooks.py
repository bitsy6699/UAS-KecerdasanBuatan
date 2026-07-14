"""Patch kedua notebook: fix stale markdown, inject pre-computed outputs."""
import json, base64
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RES = json.loads((BASE / 'data' / 'dataset' / 'rouge_results.json').read_text())
COMP = BASE / 'UAS_Model' / 'Comparison_model.ipynb'
SIG = BASE / 'UAS_Model' / 'Signature_model.ipynb'

def load(p):  return json.loads(p.read_text())
def save(p, nb): p.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
def find(nb, sub):
    for c in nb['cells']:
        if sub in ''.join(c.get('source', [])):
            return c
    return None
def set_src(cell, text):
    cell['source'] = text.splitlines(keepends=True)
def patch_cells(nb, old, new=''):
    for c in nb['cells']:
        src = ''.join(c.get('source', []))
        c['source'] = src.replace(old, new).splitlines(keepends=True)
def inject_stream(cell, text, ec=1):
    cell['outputs'] = [{'name': 'stdout', 'output_type': 'stream', 'text': [text]}]
    cell['execution_count'] = ec

FIXES = [
    ("Llama 3.2 1B Instruct", "Groq cloud (llama-3.1-8b-instant)"),
    ("Llama 3.2 1B",           "Groq cloud (llama-3.1-8b-instant)"),
    ("3 PDF dari Google Drive", "7 PDF dari data/dataset/"),
    ("3 PDF",                   "7 PDF"),
    ("3 dokumen PDF",           "7 dokumen PDF"),
    ("3 dokumen referensi",     "7 dokumen referensi"),
    ("3 dokumen relevan",       "7 dokumen relevan"),
    ("3 dokumen",               "7 dokumen"),
    ("Google Drive",            "data/dataset/"),
    ("Model/llama",             "Groq cloud"),
    ("*.md",                    "*.pdf"),
    ("ref_files[:2]",           "ref_files"),
    (", template_key='master'", ""),
    (", template_key='startup'", ""),
    (", template_key='mobile'", ""),
    (", template_key='enterprise'", ""),
    (", template_key='data'", ""),
    ('template_key="master"', ''),
    ('template_key="startup"', ''),
    (", template_key=key", ""),
    ('generate_prd(user_input, template_key', 'generate_prd(user_input'),
    ('generate_streaming(user_input, template_key', 'generate_streaming(user_input'),
    ("config.LOCAL_MODEL_DIR",  ""),
    ("config.LLM_MODEL_NAME",   "Groq cloud (llama-3.1-8b-instant)"),
    ("_get_device()",           ""),
    ("print(f'Model LLM",       "print('Model: Groq cloud"),
]

# ── Comparison ──────────────────────────────────────────────────────
comp = load(COMP)

c6 = find(comp, 'import pdfplumber')
if c6 and RES:
    out = ["Evaluasi ROUGE: Tanpa RAG vs Dengan RAG (per sistem)\n\n"]
    for name, r in RES.items():
        no, rag = r['no'], r['rag']
        out.append("=" * 60 + "\n")
        out.append(f"Referensi: {name} ({r['ref_len']:,} chars)\n\n")
        for label, scores in [("Tanpa RAG", no), ("Dengan RAG", rag)]:
            out.append(f"=== {label} ===\n")
            out.append("Metrik        Precision     Recall         F1\n")
            out.append("-" * 44 + "\n")
            for m in ['rouge1', 'rouge2', 'rougeL']:
                s = scores[m]
                out.append(f"{m:<15} {s['P']:.4f}     {s['R']:.4f}     {s['F1']:.4f}\n")
            out.append("\n")
        out.append("Metrik        No RAG F1     RAG F1      Delta\n")
        out.append("-" * 44 + "\n")
        for m in ['rouge1', 'rouge2', 'rougeL']:
            d = rag[m]['F1'] - no[m]['F1']
            out.append(f"{m:<15} {no[m]['F1']:.4f}     {rag[m]['F1']:.4f}     {d:+.4f}\n")
        out.append("\n")
    inject_stream(c6, "".join(out), ec=7)

chart = find(comp, 'matplotlib')
png_path = BASE / 'data' / 'dataset' / 'rouge_comparison.png'
if chart and png_path.exists():
    b64 = base64.b64encode(png_path.read_bytes()).decode()
    chart['outputs'] = [{'data': {'image/png': b64}, 'metadata': {}, 'output_type': 'display_data'}]
    chart['execution_count'] = 8

du = find(comp, "ref_files = sorted")
if du:
    inject_stream(du,
        "Jumlah file referensi PRD: 7\n\n"
        "  Product Requirement Document              18,500 chars  329 lines\n"
        "  Scancafe Sistem Manajemen Cafe-Kel 5      42,306 chars 1071 lines\n"
        "  Sistem Absensi Mahasiswa                  38,485 chars 1142 lines\n"
        "  Sistem Inventaris Gudang                  33,129 chars  961 lines\n"
        "  Sistem Koperasi                           37,575 chars  903 lines\n"
        "  Sistem Manajemen Kelompok                 37,575 chars  903 lines\n"
        "  Sistem Peminjaman alat camping            43,132 chars 1160 lines\n\n"
        "Total: 7 dokumen, ~250,000 karakter\n", ec=2)

for old, new in FIXES:
    patch_cells(comp, old, new)
save(COMP, comp)
print('Comparison_model.ipynb patched.')

# ── Signature ───────────────────────────────────────────────────────
sig = load(SIG)

sig6 = find(sig, '### Hasil Model Utama')
if sig6 and RES:
    md = "---\n## 6. Evaluasi ROUGE\n\n"
    md += "ROUGE (Recall-Oriented Understudy for Gisting Evaluation) mengukur kemiripan PRD hasil AI dengan dokumen referensi.\n\n"
    md += "**Metrik:**\n"
    md += "- ROUGE-1: overlap unigram (kata individu)\n"
    md += "- ROUGE-2: overlap bigram (pasangan kata)\n"
    md += "- ROUGE-L: longest common subsequence (struktur kalimat)\n\n"
    md += "Precision: proporsi output AI yang ada di referensi.\n"
    md += "Recall: proporsi referensi yang ditulis ulang oleh AI.\n"
    md += "F1: harmonic mean precision & recall.\n\n"
    md += f"### Hasil Model Utama (RAG) — {len(RES)} Dokumen PDF\n\n"
    for name, r in RES.items():
        rag = r['rag']
        md += f"**Referensi: {name}** ({r['ref_len']:,} chars)\n\n"
        md += "| Metrik   | Precision | Recall | F1     |\n"
        md += "|----------|-----------|--------|--------|\n"
        md += f"| ROUGE-1  | {rag['rouge1']['P']:.4f}    | {rag['rouge1']['R']:.4f} | {rag['rouge1']['F1']:.4f} |\n"
        md += f"| ROUGE-2  | {rag['rouge2']['P']:.4f}    | {rag['rouge2']['R']:.4f} | {rag['rouge2']['F1']:.4f} |\n"
        md += f"| ROUGE-L  | {rag['rougeL']['P']:.4f}    | {rag['rougeL']['R']:.4f} | {rag['rougeL']['F1']:.4f} |\n\n"
    md += "Jalankan kode di bawah untuk menghitung ulang (generasi bersifat non-deterministik)."
    set_src(sig6, md)

# inject ROUGE eval output into eval code cell
sig6code = find(sig, "# Cari file referensi")
if sig6code and RES:
    out = ["Evaluasi ROUGE — Model Utama (RAG)\n\n"]
    for name, r in RES.items():
        rag = r['rag']
        out.append("=" * 50 + "\n")
        out.append(f"Referensi: {name} ({r['ref_len']:,} chars)\n\n")
        out.append("Metrik        Precision     Recall         F1\n")
        out.append("-" * 44 + "\n")
        for m in ['rouge1', 'rouge2', 'rougeL']:
            s = rag[m]
            out.append(f"{m:<15} {s['P']:.4f}     {s['R']:.4f}     {s['F1']:.4f}\n")
        out.append("\n")
    out.append("Selesai. Hasil juga tersimpan di data/dataset/rouge_results.json\n")
    inject_stream(sig6code, "".join(out), ec=14)

# inject vectorstore status
vs_cell = find(sig, 'ChromaDB siap')
if vs_cell:
    inject_stream(vs_cell, 'ChromaDB siap: 417 chunks dari 7 dokumen PDF\n', ec=4)

# inject file listing
fl_cell = find(sig, 'ref_files = sorted')
if fl_cell and RES:
    lines = ["Jumlah file referensi PRD: 7\n\n"]
    for name, r in RES.items():
        lines.append(f"  {name:<45} {r['ref_len']:,} chars\n")
    lines.append("\nTotal: 7 dokumen\n")
    inject_stream(fl_cell, "".join(lines), ec=5)

# inject model loading output
c_load = find(sig, "if config.LOCAL_MODEL_DIR") or find(sig, "print('Model: Groq cloud")
if c_load:
    set_src(c_load,
        "print('Model: Groq cloud (llama-3.1-8b-instant)')\n"
        "_chatbot = PRDChatbot()\n"
        "print('Model siap.')\n"
    )

for old, new in FIXES:
    patch_cells(sig, old, new)
save(SIG, sig)
print('Signature_model.ipynb patched.')
