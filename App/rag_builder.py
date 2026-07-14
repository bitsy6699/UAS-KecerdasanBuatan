import json, os, glob, re, shutil
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from App import config

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
    """Delete existing vectorstore and rebuild from local dataset."""
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
