import json, os, glob, re, shutil
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from App import config

GDRIVE_FILES = [
    ('1810W6mePvPXGTSHCE45lglP3u9Reu2Cu', 'pemodelan dfd.pdf'),
    ('1agz4t1lDjCUyp4Oy7jKbKfxiC0ZcxEGU', 'Pengenalan UML.pptx'),
    ('1QjnoTOFR_SuzjEZa2kNgSjau0qRweXMj', 'Pengujian Perangkat Lunak.pptx'),
    ('1uBO-_lTJ_6SUwIAJblxLPrQbE-9Nf_FT', 'Pertemuan 3.pptx'),
    ('1Fry_p5MBfWFB1wigMssOwtY8xjNZpg7p', 'Pertemuan 5.pptx'),
    ('1iQKsekVeoWqTuh5BjYzevWEKcUIEos5w', 'Scancafe Sistem Manajemen Cafe-Kel 5.pdf'),
    ('1YjPvkq14klPlDocDfmtf60DfLaukAhpD', 'Sistem Absensi Mahasiswa.pdf'),
    ('1eOkq9-N5-POI7WKbIWi6NFbHc0DMTofp', 'Sistem Inventaris Gudang.pdf'),
    ('1lozLev3i1bEectXiNdLk0xE5LyVXTyw4', 'Sistem Koperasi.pdf'),
    ('1aXh7bPzuR-GR01r4w9fx1JIvhTqAqcM4', 'Sistem Manajemen Kelompok.pdf'),
    ('1JkwnDnYyrW2kXoCSqWsHbqXB5mVxTM8K', 'Sistem Peminjaman alat camping.pdf'),
    ('1DDDainD2wOpYQU-rnYPn-tUyr_5Z3lcx', '[EXAMPLE] PRD - Articles.pdf'),
    ('1fmFX_H5cYo8T59KzvasC_-2Ovhfg7SYr', '[TEMPLATE] PRD - Articles.docx'),
    # Data PRD baru dari user
    ('183xk1WoFZ_TxCWyf8AYQbDiexyfIH6LT', 'PRD_Aplikasi_Pemesanan_Makanan.md'),
    ('12iKmQt4EW9LcS_2I_X7myLp9-4LPdosm', 'PRD_Gerak_Aplikasi_Fitness.md'),
    ('1sCp4SanFMYF41BoiXVIAKQiuv0UUT16s', 'PRD_Hijau_Aplikasi_Lingkungan.md'),
    ('1MDBS4YQnIiPhUBZssq9ObI3-CNAi5ANc', 'PRD_Jalan_Aplikasi_Travel.md'),
    ('1yGD44BPOoueLuKiC-GbmaJmHFHXUFshf', 'PRD_Pintar_Aplikasi_Edukasi.md'),
    ('1-eThsJGu6mOu5JM85SMUwaw_4hMZUeEJ', 'PRD_Sakuku_Dompet_Digital.md'),
    ('1kodMrLje2onQKTWr_R1cfn9Qg0CIHpXu', 'PRD_Sistem_Perpustakaan_Digital.md'),
    ('1CJe8mGp0PrIde6mTOlif2gRbQ36aKTdq', 'PRD_Tenang_Aplikasi_Kesehatan_Mental.md'),
    ('19_5EDoeL3vEHeZ8vFLMoGbd1h6sB-08y', 'Product Requirement Document.pdf'),
]


def _download_from_drive():
    """Download all files from Google Drive folder."""
    if config.TEMP_DRIVE_DIR.exists():
        shutil.rmtree(config.TEMP_DRIVE_DIR)
    config.TEMP_DRIVE_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import gdown
        print(f'Downloading from Google Drive (folder: {config.GDRIVE_FOLDER_ID})...')
        gdown.download_folder(
            id=config.GDRIVE_FOLDER_ID,
            output=str(config.TEMP_DRIVE_DIR),
            quiet=False,
        )
        print('Download selesai.')
    except Exception as e:
        print(f'gdown gagal ({e}), beralih ke requests fallback...')
        import requests as req
        for fid, fname in GDRIVE_FILES:
            dest = config.TEMP_DRIVE_DIR / fname
            if dest.exists():
                continue
            url = f'https://drive.usercontent.google.com/download?id={fid}&export=download'
            print(f'  Downloading {fname}...')
            try:
                r = req.get(url, stream=True, timeout=30)
                if r.status_code == 200:
                    with open(dest, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f'    Saved {dest.stat().st_size:,} bytes')
                else:
                    print(f'    Failed: HTTP {r.status_code}')
            except Exception as ex:
                print(f'    Error: {ex}')
        print('Download selesai (fallback).')


EXCLUDE_PATTERNS = [
    'pertemuan 3',
    'pertemuan 5'
]

def _is_excluded(filename: str) -> bool:
    name = filename.lower().replace('.pdf', '').replace('.pptx', '').replace('.md', '')
    return any(p in name for p in EXCLUDE_PATTERNS)

def _build_documents(src_dir: Path) -> list:
    """Read PDFs from src_dir, extract text in-memory, return list of Document chunks."""
    import pdfplumber

    all_chunks = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=['\n\n', '\n', '. ', ' ']
    )

    for f_path in sorted(glob.glob(str(src_dir / '*.pdf'))):
        fname = os.path.basename(f_path)
        if _is_excluded(fname):
            print(f'  Skipping {fname} (excluded)')
            continue
        try:
            with pdfplumber.open(str(f_path)) as pdf:
                pages = [p.extract_text() or '' for p in pdf.pages]
            content = '\n\n'.join(pages)
        except Exception as e:
            print(f'  Error reading {fname}: {e}')
            continue
        if not content.strip():
            continue
        print(f'  Processing {fname} ({len(content):,} chars)')
        chunks = splitter.split_text(content)
        for i, chunk in enumerate(chunks):
            section = ''
            match = re.search(r'(\d+[\.\d]*\s+[A-Za-z].*?)(?:\n|$)', chunk)
            if match:
                section = match.group(1).strip()
            all_chunks.append(Document(
                page_content=chunk,
                metadata={'source': fname, 'section': section, 'chunk_id': i}
            ))
    return all_chunks


def build_vectorstore():
    """Build vectorstore from local PDFs in data/dataset/ (no intermediate .md files)."""
    local_docs = _build_documents(config.DATA_RAW) if config.DATA_RAW.exists() else []

    all_docs = local_docs
    if not all_docs:
        print('Tidak ada dokumen ditemukan di data/dataset/.')
        return None

    emb = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL, model_kwargs={'local_files_only': True})
    store = Chroma.from_documents(
        documents=all_docs,
        embedding=emb,
        persist_directory=str(config.VECTORSTORE_DIR),
        collection_name=config.CHROMA_COLLECTION_NAME
    )
    print(f'Vectorstore built with {len(all_docs)} chunks dari data/dataset/')
    return store


def rebuild_vectorstore():
    """Delete existing vectorstore and rebuild from Drive."""
    if config.VECTORSTORE_DIR.exists():
        shutil.rmtree(config.VECTORSTORE_DIR)
        print('Existing vectorstore deleted.')
    return build_vectorstore()


def get_vectorstore():
    """Return existing vectorstore or build if not exists."""
    if config.VECTORSTORE_DIR.exists():
        emb = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL, model_kwargs={'local_files_only': True})
        return Chroma(
            embedding_function=emb,
            persist_directory=str(config.VECTORSTORE_DIR),
            collection_name=config.CHROMA_COLLECTION_NAME
        )
    return build_vectorstore()


if __name__ == '__main__':
    build_vectorstore()
