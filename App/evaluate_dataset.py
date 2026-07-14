import sys, os, time, json, shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'App'))

import config
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from rouge_score import rouge_scorer
import pdfplumber

from rag_builder import rebuild_vectorstore
from chatbot import PRDChatbot

# 1) Rebuild vectorstore murni dari 7 PDF di data/dataset/
if config.VECTORSTORE_DIR.exists():
    shutil.rmtree(config.VECTORSTORE_DIR)
vs = rebuild_vectorstore()
print(f'Vectorstore ready: {bool(vs)}')

# 2) Load chatbot (cloud API atau lokal)
chatbot = PRDChatbot()

raw_dir = BASE_DIR / 'data' / 'dataset'

def _read_pdf_text(pdf_path: Path) -> str:
    with pdfplumber.open(str(pdf_path)) as pdf:
        pages = [p.extract_text() or '' for p in pdf.pages]
    return '\n\n'.join(pages)


# Sistem -> (nama referensi, file PDF referensi, prompt generasi)
SYSTEMS = [
    ('Sistem Manajemen Cafe', 'Scancafe Sistem Manajemen Cafe-Kel 5.pdf',
     'Buat PRD lengkap untuk sistem manajemen cafe'),
    ('Sistem Koperasi', 'Sistem Koperasi.pdf',
     'Buat PRD lengkap untuk sistem koperasi'),
    ('Sistem Inventaris Gudang', 'Sistem Inventaris Gudang.pdf',
     'Buat PRD lengkap untuk sistem inventaris gudang'),
    ('Sistem Absensi Mahasiswa', 'Sistem Absensi Mahasiswa.pdf',
     'Buat PRD lengkap untuk sistem absensi mahasiswa'),
    ('Sistem Manajemen Kelompok', 'Sistem Manajemen Kelompok.pdf',
     'Buat PRD lengkap untuk sistem manajemen kelompok'),
    ('Sistem Peminjaman Alat Camping', 'Sistem Peminjaman alat camping.pdf',
     'Buat PRD lengkap untuk sistem peminjaman alat camping'),
    ('Product Requirement Document', 'Product Requirement Document.pdf',
     'Buat PRD lengkap berdasarkan dokumen requirement produk'),
]

def evaluate_rouge(hypothesis, reference):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    s = scorer.score(reference, hypothesis)
    return {
        'rouge1': {'P': s['rouge1'].precision, 'R': s['rouge1'].recall, 'F1': s['rouge1'].fmeasure},
        'rouge2': {'P': s['rouge2'].precision, 'R': s['rouge2'].recall, 'F1': s['rouge2'].fmeasure},
        'rougeL': {'P': s['rougeL'].precision, 'R': s['rougeL'].recall, 'F1': s['rougeL'].fmeasure},
    }


print('\nEvaluasi ROUGE: Tanpa RAG vs Dengan RAG (per sistem)\n')
RESULTS = {}
for name, fname, prompt in SYSTEMS:
    ref_text = _read_pdf_text(raw_dir / fname)
    t0 = time.time()
    hasil_no_rag = chatbot.generate_no_rag(prompt)
    t_no = time.time() - t0
    t0 = time.time()
    hasil_rag = chatbot.generate_prd(prompt)
    t_rag = time.time() - t0

    s_no = evaluate_rouge(hasil_no_rag, ref_text)
    s_rag = evaluate_rouge(hasil_rag, ref_text)
    RESULTS[name] = {'no': s_no, 'rag': s_rag, 'ref_len': len(ref_text),
                     'no_len': len(hasil_no_rag), 'rag_len': len(hasil_rag),
                     't_no': round(t_no, 1), 't_rag': round(t_rag, 1)}

    print(f"\n{'='*60}")
    print(f"Referensi: {name} ({len(ref_text):,} chars)")
    print(f"  [Tanpa RAG] {len(hasil_no_rag):,} chars | {t_no:.1f}s")
    print(f"  [Dengan RAG] {len(hasil_rag):,} chars | {t_rag:.1f}s")
    for m in ['rouge1', 'rouge2', 'rougeL']:
        d = s_rag[m]['F1'] - s_no[m]['F1']
        print(f"  {m:<9} NoRAG F1={s_no[m]['F1']:.4f}  RAG F1={s_rag[m]['F1']:.4f}  Delta={d:+.4f}")

# 3) Chart perbandingan ROUGE F1
metrics = ['rouge1', 'rouge2', 'rougeL']
disp = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L']
names = list(RESULTS.keys())
fig, axes = plt.subplots(1, len(names), figsize=(5 * len(names), 5))
for ax, name in zip(axes, names):
    r = RESULTS[name]
    f1_no = [r['no'][m]['F1'] for m in metrics]
    f1_rag = [r['rag'][m]['F1'] for m in metrics]
    x = np.arange(len(metrics)); w = 0.35
    ax.bar(x - w/2, f1_no, w, label='Tanpa RAG', color='#e74c3c', alpha=0.8)
    ax.bar(x + w/2, f1_rag, w, label='Dengan RAG', color='#2ecc71', alpha=0.8)
    ax.set_title(f'Vs {name}', fontsize=12)
    ax.set_xticks(x); ax.set_xticklabels(disp, fontsize=9)
    ax.set_ylim(0, max(max(f1_no), max(f1_rag)) + 0.1)
    ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3)
    for bars in ax.containers:
        for bar in bars:
            ax.annotate(f'{bar.get_height():.3f}', xy=(bar.get_x()+bar.get_width()/2, bar.get_height()),
                        xytext=(0, 2), textcoords='offset points', ha='center', fontsize=7)
fig.suptitle('Perbandingan ROUGE F1-Score: Tanpa RAG vs Dengan RAG', fontsize=14)
plt.tight_layout()
plt.savefig(str(BASE_DIR / 'data' / 'dataset' / 'rouge_comparison.png'), dpi=150)
plt.close()
print('\nGrafik saved to data/dataset/rouge_comparison.png')

# 4) EDA chart: ukuran referensi & chunk per sistem
ref_lens = [RESULTS[n]['ref_len'] for n in names]
chunk_counts = []
for n in names:
    # hitung chunk kasar (~800 chars) sebagai proxy EDA
    chunk_counts.append(max(1, RESULTS[n]['ref_len'] // 800))
fig, ax1 = plt.subplots(figsize=(8, 5))
x = np.arange(len(names)); w = 0.35
ax1.bar(x - w/2, ref_lens, w, label='Karakter referensi', color='#3498db')
ax1.set_ylabel('Karakter', color='#3498db')
ax1.set_xticks(x); ax1.set_xticklabels(names, fontsize=9)
ax2 = ax1.twinx()
ax2.bar(x + w/2, chunk_counts, w, label='~Chunk (800 char)', color='#9b59b6')
ax2.set_ylabel('~Chunk', color='#9b59b6')
ax1.set_title('EDA Dataset: 7 Dokumen PDF')
fig.tight_layout()
plt.savefig(str(BASE_DIR / 'data' / 'dataset' / 'eda_dataset.png'), dpi=150)
plt.close()
print('Grafik saved to data/dataset/eda_dataset.png')

# 5) Simpan hasil JSON
out = {n: {k: v for k, v in r.items()} for n, r in RESULTS.items()}
(BASE_DIR / 'data' / 'dataset' / 'rouge_results.json').write_text(json.dumps(out, indent=2, ensure_ascii=False))
print('Hasil tersimpan di data/dataset/rouge_results.json')
