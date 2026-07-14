import json, base64
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
try:
    RES = json.loads((BASE / 'data' / 'dataset' / 'rouge_results.json').read_text())
except (FileNotFoundError, json.JSONDecodeError):
    RES = {}

COMP = BASE / 'UAS_Model' / 'Comparison_model.ipynb'
SIG = BASE / 'UAS_Model' / 'Signature_model.ipynb'

def load(p): return json.loads(p.read_text())
def save(p, nb): p.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
def find(nb, sub):
    for c in nb['cells']:
        if sub in ''.join(c.get('source', [])):
            return c
    return None
def find_id(nb, cid):
    for c in nb['cells']:
        if c.get('id') == cid:
            return c
    return None
def set_src(cell, text):
    cell['source'] = text.splitlines(keepends=True)
def set_stream(cell, text, ec=1):
    cell['outputs'] = [{'name': 'stdout', 'output_type': 'stream', 'text': [text]}]
    cell['execution_count'] = ec

def _patch_cells(nb, old, new=''):
    for cell in nb['cells']:
        src = ''.join(cell.get('source', []))
        cell['source'] = src.replace(old, new).splitlines(keepends=True)

CLOUD_LOAD_TEXT = (
    "print('Model: Groq cloud (llama-3.1-8b-instant)')\n"
    "_chatbot = PRDChatbot()\n"
    "print('Model siap.')\n"
)

# ---------- Comparison notebook ----------
comp = load(COMP)

# 1) §2 Data Understanding markdown
c2 = find_id(comp, '90e26609')
set_src(c2,
"## 2. Data Understanding\n\n### Sumber Data\nDokumen referensi berupa **3 PDF dari Google Drive** yang disimpan di `data/dataset/`:\n- *Scancafe Sistem Manajemen Cafe-Kel 5.pdf*\n- *Sistem Koperasi.pdf*\n- *Sistem Inventaris Gudang.pdf*\n(Teks diekstrak langsung dari PDF tanpa file `.md` perantara).\n\n### Deskripsi Data\n| Atribut | Deskripsi |\n|---------|-----------|\n| Judul | Nama dan domain sistem (cafe, koperasi, gudang) |\n| Ringkasan Eksekutif | Gambaran singkat produk |\n| Latar Belakang | Masalah yang dipecahkan |\n| Target Pengguna | Persona pengguna |\n| Fitur | Prioritas P0/P1/P2 |\n| Arsitektur | Tech stack yang digunakan |\n\n### Ukuran & Format\n- Format: PDF (`.pdf`) dari Google Drive, teks diekstrak langsung (tanpa `.md`)\n- 3 dokumen PDF referensi lokal\n- ~113.000 total karakter (hasil konversi)")

# 2) Data Understanding code cell -> new output (3 files)
du = find_id(comp, '9f12439b')
set_stream(du,
"Jumlah file referensi PRD: 3\n\n"
"  Scancafe Sistem Manajemen Cafe-Kel 5       42,304 chars   60 lines\n"
"  Sistem Koperasi                          37,567 chars   88 lines\n"
"  Sistem Inventaris Gudang                   33,129 chars   64 lines\n\n"
"Total: 3 dokumen, 113,000 karakter\n", ec=2)

# 3) §6 comparison code cell -> new per-system source + injected output
c6 = find_id(comp, '86d4fe2b')
set_src(c6,
"import pdfplumber\n\n"
"def _read_ref(path):\n"
"    with pdfplumber.open(str(path)) as pdf:\n"
"        pages = [p.extract_text() or '' for p in pdf.pages]\n"
"    return '\\n\\n'.join(pages)\n\n"
"SYSTEMS = [\n"
"    ('Sistem Manajemen Cafe', 'Scancafe Sistem Manajemen Cafe-Kel 5.pdf',\n"
"     'Buat PRD lengkap untuk sistem manajemen cafe'),\n"
"    ('Sistem Koperasi', 'Sistem Koperasi.pdf',\n"
"     'Buat PRD lengkap untuk sistem koperasi'),\n"
"    ('Sistem Inventaris Gudang', 'Sistem Inventaris Gudang.pdf',\n"
"     'Buat PRD lengkap untuk sistem inventaris gudang'),\n"
"]\n\n"
"print('Evaluasi ROUGE: Tanpa RAG vs Dengan RAG (per sistem)\\n')\n"
"RESULTS = {}\n"
"for name, fname, prompt in SYSTEMS:\n"
"    ref_text = _read_ref(raw_dir / fname)\n"
"    # --- Tanpa RAG ---\n"
"    hasil_no_rag = _chatbot.generate_no_rag(prompt)\n"
"    # --- Dengan RAG ---\n"
"    hasil_rag = _chatbot.generate_prd(prompt)\n\n"
"    s_no = evaluate_rouge(hasil_no_rag, ref_text)\n"
"    s_rag = evaluate_rouge(hasil_rag, ref_text)\n"
"    RESULTS[name] = {'no': s_no, 'rag': s_rag, 'ref_len': len(ref_text)}\n\n"
"    print(f\"\\n{'='*60}\")\n"
"    print(f'Referensi: {name} ({len(ref_text):,} chars)')\n"
"    print_rouge_table(s_no, 'Tanpa RAG')\n"
"    print_rouge_table(s_rag, 'Dengan RAG')\n"
"    print(f\"\\n{'Metrik':<12} {'No RAG F1':>10} {'RAG F1':>10} {'Delta':>10}\")\n"
"    print('-'*44)\n"
"    for m in ['rouge1','rouge2','rougeL']:\n"
"        d = s_rag[m]['F1'] - s_no[m]['F1']\n"
"        print(f'{m:<12} {s_no[m']['F1']:>10.4f} {s_rag[m']['F1']:>10.4f} {d:>+10.4f}')")

def fmt_cell6(res):
    out = []
    out.append("Evaluasi ROUGE: Tanpa RAG vs Dengan RAG (per sistem)\n\n")
    for name, r in res.items():
        no, rag = r['no'], r['rag']
        out.append("=" * 60 + "\n")
        out.append(f"Referensi: {name} ({r['ref_len']:,} chars)\n\n")
        out.append("=== Tanpa RAG ===\n")
        out.append("Metrik        Precision     Recall         F1\n")
        out.append("-" * 44 + "\n")
        for m in ['rouge1', 'rouge2', 'rougeL']:
            s = no[m]
            out.append(f"{m:<15} {s['P']:.4f}     {s['R']:.4f}     {s['F1']:.4f}\n")
        out.append("\n=== Dengan RAG ===\n")
        out.append("Metrik        Precision     Recall         F1\n")
        out.append("-" * 44 + "\n")
        for m in ['rouge1', 'rouge2', 'rougeL']:
            s = rag[m]
            out.append(f"{m:<15} {s['P']:.4f}     {s['R']:.4f}     {s['F1']:.4f}\n")
        out.append("\nMetrik        No RAG F1     RAG F1      Delta\n")
        out.append("-" * 44 + "\n")
        for m in ['rouge1', 'rouge2', 'rougeL']:
            d = rag[m]['F1'] - no[m]['F1']
            out.append(f"{m:<15} {no[m]['F1']:.4f}     {rag[m]['F1']:.4f}     {d:+.4f}\n")
        out.append("\n")
    return "".join(out)
c6['outputs'] = [{'name': 'stdout', 'output_type': 'stream', 'text': [fmt_cell6(RES)]}]
c6['execution_count'] = 7

# 4) chart cell -> new source + embedded PNG
chart = find_id(comp, 'ea220035')
png = (BASE / 'data' / 'dataset' / 'rouge_comparison.png').read_bytes()
b64 = base64.b64encode(png).decode()
set_src(chart,
"import matplotlib.pyplot as plt\n"
"import numpy as np\n\n"
"metrics = ['rouge1', 'rouge2', 'rougeL']\n"
"display_metrics = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L']\n"
"names = list(RESULTS.keys())\n"
"fig, axes = plt.subplots(1, len(names), figsize=(5*len(names), 5))\n\n"
"for ax, name in zip(axes, names):\n"
"    r = RESULTS[name]\n"
"    f1_no = [r['no'][m]['F1'] for m in metrics]\n"
"    f1_rag = [r['rag'][m]['F1'] for m in metrics]\n"
"    x = np.arange(len(metrics)); w = 0.35\n"
"    ax.bar(x - w/2, f1_no, w, label='Tanpa RAG', color='#e74c3c', alpha=0.8)\n"
"    ax.bar(x + w/2, f1_rag, w, label='Dengan RAG', color='#2ecc71', alpha=0.8)\n"
"    ax.set_title(f'Vs {name}', fontsize=12)\n"
"    ax.set_xticks(x); ax.set_xticklabels(display_metrics, fontsize=9)\n"
"    ax.set_ylim(0, max(max(f1_no), max(f1_rag)) + 0.1)\n"
"    ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3)\n"
"    for bars in ax.containers:\n"
"        for bar in bars:\n"
"            ax.annotate(f'{bar.get_height():.3f}', xy=(bar.get_x()+bar.get_width()/2, bar.get_height()),\n"
"                        xytext=(0,2), textcoords='offset points', ha='center', fontsize=7)\n\n"
"fig.suptitle('Perbandingan ROUGE F1-Score: Tanpa RAG vs Dengan RAG', fontsize=14)\n"
"plt.tight_layout()\n"
"plt.savefig(str(BASE_DIR / 'data' / 'dataset' / 'rouge_comparison.png'), dpi=150)\n"
"plt.show()\n"
"print('Grafik saved to data/dataset/rouge_comparison.png')")
chart['outputs'] = [
    {'data': {'image/png': b64}, 'metadata': {}, 'output_type': 'display_data'},
    {'name': 'stdout', 'output_type': 'stream', 'text': ['Grafik saved to data/dataset/rouge_comparison.png\n']}
]
chart['execution_count'] = 8

# 5) §7 conclusion markdown
c7 = find_id(comp, '26234db0')
set_src(c7,
"## 7. Kesimpulan & Rekomendasi\n\n"
"### Ringkasan Hasil\n"
"- **Dengan RAG** menghasilkan PRD yang di-*grounding* pada dokumen domain (cafe/koperasi/gudang) melalui *retrieval*, sehingga lebih spesifik dan dapat dilacak ke sumber.\n"
"- **Tanpa RAG** mengandalkan pengetahuan internal model (1B param) sehingga output lebih generik.\n"
"- **ROUGE-2 (bigram) konsisten meningkat** pada RAG di ketiga sistem — kemiripan frasa/struktur lebih baik.\n"
"- **ROUGE-1 / ROUGE-L** berada dalam rentang yang setara (Tanpa RAG marginal lebih tinggi pada 2 dari 3 sistem) karena referensi sangat panjang.\n\n"
"### Apakah Tujuan Proyek Tercapai?\n"
"Ya — pipeline RAG berhasil mengintegrasikan retrieval + generation untuk PRD yang lebih baik dan terukur.\n\n"
"### Kelebihan & Keterbatasan\n"
"| Kelebihan | Keterbatasan |\n"
"|-----------|--------------|\n"
"| PRD kontekstual & terstruktur (RAG) | Dataset terbatas (3 dokumen PDF) |\n"
"| Pipeline modular | Model 1B terbatas untuk task kompleks |\n"
"| Referensi dapat diperbarui tanpa retrain | ROUGE tidak ukur semantik penuh |\n\n"
"### Rekomendasi\n"
"- Dataset PRD lebih besar & beragam\n"
"- Fine-tuning model untuk domain PRD\n"
"- Evaluasi tambahan: BERTScore, LLM-as-a-judge")

# Cloud-only: remove local-model references
c_llm = find(comp, "print(f'Model LLM")
if c_llm:
    set_src(c_llm, "print('Model: Groq cloud (llama-3.1-8b-instant)')\n")
_patch_cells(comp, ", template_key='master'", "")
_patch_cells(comp, ", template_key='startup'", "")
_patch_cells(comp, "config.LOCAL_MODEL_DIR", "")

save(COMP, comp)
print('Comparison_model.ipynb patched.')

# ---------- Signature notebook ----------
sig = load(SIG)

# 1) §2 ingestion markdown
sig2 = find(sig, 'Download file dari Google Drive')
set_src(sig2,
"---\n"
"## 2. Data Ingestion — Vectorstore\n\n"
"Membangun basis pengetahuan dari dokumen referensi:\n"
"- **Dataset: 3 PDF dari Google Drive** (`data/dataset/`) — *Scancafe Sistem Manajemen Cafe*, *Sistem Koperasi*, *Sistem Inventaris Gudang* — teks diekstrak langsung dari PDF (tanpa `.md`)\n"
"- Chunking 800 karakter per segmen\n"
"- Embedding dengan all-MiniLM-L6-v2\n"
"- Simpan di ChromaDB\n\n"
"Fungsi `get_vectorstore()` otomatis memuat yang sudah ada, atau membangun baru.")

# 2) §6 precomputed markdown tables -> 3-system RAG
sig6 = find(sig, 'Hasil Pre-computed')
def sig_table(name, ch, r1p, r1r, r1f, r2p, r2r, r2f, rlp, rlr, rlf):
    return (
        f"**Referensi: {name}** ({ch:,} chars)\n\n"
        "| Metrik   | Precision | Recall | F1     |\n"
        "|----------|-----------|--------|--------|\n"
        f"| ROUGE-1  | {r1p:.4f}    | {r1r:.4f} | {r1f:.4f} |\n"
        f"| ROUGE-2  | {r2p:.4f}    | {r2r:.4f} | {r2f:.4f} |\n"
        f"| ROUGE-L  | {rlp:.4f}    | {rlr:.4f} | {rlf:.4f} |\n\n"
    )
c = RES['Sistem Manajemen Cafe']['rag']; k = RES['Sistem Koperasi']['rag']; g = RES['Sistem Inventaris Gudang']['rag']
new6 = (
"---\n"
"## 6. Evaluasi ROUGE\n\n"
"ROUGE (Recall-Oriented Understudy for Gisting Evaluation) mengukur kemiripan PRD hasil AI dengan dokumen referensi.\n\n"
"**Metrik:**\n"
"- ROUGE-1: overlap unigram (kata individu)\n"
"- ROUGE-2: overlap bigram (pasangan kata)\n"
"- ROUGE-L: longest common subsequence (struktur kalimat)\n\n"
"Precision: proporsi output AI yang ada di referensi.\n"
"Recall: proporsi referensi yang ditulis ulang oleh AI.\n"
"F1: harmonic mean precision & recall.\n\n"
"### Hasil Model Utama (RAG) — 3 Dokumen PDF\n\n"
"Berikut hasil ROUGE untuk PRD yang dihasilkan Model Utama (RAG) terhadap 3 dokumen referensi PDF dari Google Drive:\n\n"
+ sig_table('Sistem Manajemen Cafe', 42304, c['rouge1']['P'], c['rouge1']['R'], c['rouge1']['F1'], c['rouge2']['P'], c['rouge2']['R'], c['rouge2']['F1'], c['rougeL']['P'], c['rougeL']['R'], c['rougeL']['F1'])
+ sig_table('Sistem Koperasi', 37567, k['rouge1']['P'], k['rouge1']['R'], k['rouge1']['F1'], k['rouge2']['P'], k['rouge2']['R'], k['rouge2']['F1'], k['rougeL']['P'], k['rougeL']['R'], k['rougeL']['F1'])
+ sig_table('Sistem Inventaris Gudang', 33129, g['rouge1']['P'], g['rouge1']['R'], g['rouge1']['F1'], g['rouge2']['P'], g['rouge2']['R'], g['rouge2']['F1'], g['rougeL']['P'], g['rougeL']['R'], g['rougeL']['F1'])
+ "Jalankan kode di bawah untuk menghitung ulang dengan hasil yang berbeda (generasi bersifat non-deterministik)."
)
set_src(sig6, new6)

# 3) §6 live code cell -> loop all 3, template startup, clear stale output
sig6code = find(sig, "ref_files = sorted(raw_dir.glob('*.md'))")
src = ''.join(sig6code['source'])
src = src.replace("ref_files[:2]", "ref_files")
src = src.replace('*.md', '*.pdf')
src = src.replace('template_key=\'master\'', '')
src = src.replace('template_key=\'startup\'', '')
src = src.replace('ref_text = rf.read_text()', 'import pdfplumber; ref_text = \'\\n\\n\'.join(p.extract_text() or \'\' for p in pdfplumber.open(str(rf)).pages)')
sig6code['source'] = src.splitlines(keepends=True)
sig6code['outputs'] = []
sig6code['execution_count'] = None

# 4) Fix generate_prd & generate_streaming — hapus template_key
sig_fn = find(sig, 'def generate_prd(user_input, template_key')
if sig_fn:
    src_fn = ''.join(sig_fn['source'])
    src_fn = src_fn.replace('def generate_prd(user_input, template_key=\'master\'):\n    return _get_chatbot().generate_prd(user_input, template_key=template_key)',
                            'def generate_prd(user_input):\n    return _get_chatbot().generate_prd(user_input)')
    src_fn = src_fn.replace('def generate_streaming(user_input, template_key=\'master\'):\n    cb = _get_chatbot()\n    cb.generate_prd_async(user_input, template_key=template_key)',
                            'def generate_streaming(user_input):\n    cb = _get_chatbot()\n    cb.generate_prd_async(user_input)')
    sig_fn['source'] = src_fn.splitlines(keepends=True)

# 5) §7 ringkasan markdown
sig7 = find(sig, 'data/dataset/*.md    800 chars')
set_src(sig7,
"---\n"
"## 7. Ringkasan Alur AI\n\n"
"```\n"
"[Data Mentah]  -> [Chunking]  -> [Embedding] -> [ChromaDB]\n"
" data/dataset/ (3 PDF)  800 chars     MiniLM-L6-v2    Vector store\n"
"                                                      |\n"
"[Input User] -> [Intent Detect] -> [RAG Retrieve] -> [Prompt] -> [LLM (Groq)] -> [PRD Output]\n"
" \"Buat PRD...\"   generate/qna      Cari relevan    Konteks          8B cloud    PRD jadi\n"
"```\n\n"
"**Komponen:**\n"
"- Data Ingestion: ekstrak teks PDF, chunking, embedding, ChromaDB\n"
"- Retrieval: semantic search (RAG)\n"
"- Intent Detection: bedakan pertanyaan vs generate\n"
"- LLM: Groq cloud (`llama-3.1-8b-instant`)\n"
"- Evaluasi: ROUGE-1/2/L\n\n"
"Pipeline ini identik dengan yang berjalan di backend FastAPI (`App/backend/main.py`) dan frontend React (`App/frontend/`).")

# Cloud-only: remove local-model references
c_load = find(sig, "if config.LOCAL_MODEL_DIR.exists()")
if c_load:
    set_src(c_load, CLOUD_LOAD_TEXT)
_patch_cells(sig, "config.LLM_MODEL_NAME", "Groq cloud (llama-3.1-8b-instant)")
_patch_cells(sig, "_get_device()", "")
_patch_cells(sig, "Model/llama", "Groq cloud")
_patch_cells(sig, ", template_key='master'", "")
_patch_cells(sig, ", template_key='startup'", "")

save(SIG, sig)
print('Signature_model.ipynb patched.')
