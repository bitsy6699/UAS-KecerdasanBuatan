import re
from pathlib import Path
from threading import Thread, Event

from App import config
from App.rag_builder import get_vectorstore

try:
    from openai import OpenAI
    _HAS_OPENAI = True
except ImportError:
    OpenAI = None
    _HAS_OPENAI = False


TEMPLATE_LABEL = 'Startup / MVP'

def _detect_intent(user_input: str) -> str:
    input_lower = user_input.lower()
    question_keywords = ['apa itu', 'apa sih', 'jelaskan', 'pengertian', 'definisi', 'maksudnya', 'bagaimana cara']
    example_keywords = ['contoh', 'contohkan', 'sample', 'referensi', 'tampilkan']
    recommend_keywords = ['rekomendasi', 'sarankan', 'saran', 'rekomend', 'ide', 'usulkan']
    generate_keywords = ['buatkan', 'buat', 'bikin', 'generate', 'tuliskan', 'buatkan prd']

    if any(k in input_lower for k in question_keywords):
        return 'diskusi'
    if any(k in input_lower for k in example_keywords):
        return 'example'
    if any(k in input_lower for k in recommend_keywords):
        return 'recommend'
    if any(k in input_lower for k in generate_keywords):
        return 'generate'
    return 'generate'

SYSTEM_PROMPTS = {
    'diskusi': (
        'Anda adalah asisten AI yang membantu menjelaskan konsep Product Management. '
        'Gunakan referensi yang diberikan. Jika tidak ada, jawab berdasarkan pengetahuan Anda. '
        'Berikan jawaban spesifik dan hindari kalimat generik.'
    ),
    'eksekusi': (
        'Anda adalah spesialis Product Management. Buat PRD berdasarkan referensi yang diberikan. '
        'PRD harus: spesifik, terukur (ada metrik/target), '
        'dan mencakup aspek bisnis, teknis, pengguna, dan tim. '
        'Gunakan hanya konteks yang diberikan — jangan buat asumsi. '
        'Hindari kalimat generik atau ambigu. '
        'Gunakan ## untuk header setiap bagian. Bahasa Indonesia profesional.'
    ),
    'general_knowledge': (
        'Anda adalah asisten AI yang kreatif dan berpengetahuan luas di bidang Product Management. '
        'Gunakan referensi yang diberikan sebagai acuan utama, namun Anda juga boleh '
        'menambahkan pengetahuan umum Anda untuk memperkaya jawaban. '
        'Bersikaplah seperti konsultan senior yang paham teori dan praktik. '
        'PRD harus: spesifik, terukur, mencakup aspek bisnis, teknis, pengguna, dan tim. '
        'Gunakan ## untuk header setiap bagian. Bahasa Indonesia profesional dan mengalir.'
    )
}


class PRDChatbot:
    def __init__(self):
        self.vectorstore = None
        self.client = None
        self.stop_event = Event()
        self.generation_done = Event()
        self.partial_text = ''
        self.error = None

        if config.LLM_BACKEND != 'cloud':
            raise RuntimeError(
                'Mode lokal telah dihapus. Gunakan LLM_BACKEND=cloud.'
            )
        if not _HAS_OPENAI:
            raise ImportError(
                'openai tidak terinstall. Jalankan: pip install openai'
            )
        self.client = OpenAI(
            base_url=config.LLM_API_BASE,
            api_key=config.LLM_API_KEY,
        )
        print(f'Cloud LLM: {config.LLM_API_BASE} ({config.LLM_API_MODEL})')

    def _load_vectorstore(self):
        if self.vectorstore is None:
            self.vectorstore = get_vectorstore()

    def retrieve_context(self, query: str) -> str:
        self._load_vectorstore()

        docs = self.vectorstore.similarity_search(query, k=config.RAG_TOP_K_EKSEKUSI)

        parts = []
        for d in docs:
            src = d.metadata.get('source', '-').replace('.md', '').replace('.pdf', '').replace('.pptx', '').replace('.docx', '').replace('_', ' ').title()
            parts.append(f'[{src}]\n{d.page_content.strip()}')
        return '\n\n'.join(parts)

    def _build_messages(self, user_input: str) -> list:
        intent = _detect_intent(user_input)
        context = self.retrieve_context(user_input)

        # Auto-detect: pakai general knowledge kalo referensi kosong/minim
        use_gk = len(context.strip()) < 200

        if intent == 'diskusi':
            prompt = SYSTEM_PROMPTS['general_knowledge'] if use_gk else SYSTEM_PROMPTS['diskusi']
            return [
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': (
                    f'Referensi:\n{context}\n\n{user_input}'
                )}
            ]

        prompt = SYSTEM_PROMPTS['general_knowledge'] if use_gk else SYSTEM_PROMPTS['eksekusi']

        if intent == 'example':
            return [
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': (
                    f'Referensi:\n{context}\n\n'
                    f'Buat contoh PRD untuk: {user_input}'
                )}
            ]
        elif intent == 'recommend':
            return [
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': (
                    f'Referensi:\n{context}\n\n'
                    f'Beri rekomendasi untuk: {user_input}'
                )}
            ]
        else:
            extra = '' if not use_gk else (
                '\n\nCatatan: Jika referensi terbatas, Anda boleh menggunakan '
                'pengetahuan umum Anda untuk melengkapi PRD.'
            )
            return [
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': (
                    f'Referensi:\n{context}\n\n'
                    f'Buat PRD yang spesifik dan terukur berdasarkan referensi di atas.'
                    f'{extra}\n\n'
                    f'Buat PRD untuk: {user_input}'
                )}
            ]


    def _generate_cloud(self, messages: list) -> str:
        resp = self.client.chat.completions.create(
            model=config.LLM_API_MODEL,
            messages=messages,
            temperature=0.4,
            max_tokens=config.MAX_OUTPUT_TOKENS,
            top_p=0.9,
        )
        return resp.choices[0].message.content.strip()


    def _start_cloud_generation(self, messages: list):
        self.stop_event.clear()
        self.generation_done.clear()
        self.partial_text = ''
        self.error = None

        def gen():
            try:
                resp = self.client.chat.completions.create(
                    model=config.LLM_API_MODEL,
                    messages=messages,
                    temperature=0.4,
                    max_tokens=config.MAX_OUTPUT_TOKENS,
                    top_p=0.9,
                    stream=True,
                )
                for chunk in resp:
                    if self.stop_event.is_set():
                        break
                    if chunk.choices and chunk.choices[0].delta.content:
                        self.partial_text += chunk.choices[0].delta.content
            except Exception as e:
                if not self.error:
                    self.error = str(e)
            finally:
                self.generation_done.set()

        Thread(target=gen, daemon=True).start()

    def stop(self):
        self.stop_event.set()

    def get_partial(self) -> str:
        return self.partial_text

    def is_done(self) -> bool:
        return self.generation_done.is_set()

    def get_error(self):
        return self.error

    def _save_output(self, text: str, prompt: str, mode: str):
        slug = re.sub(r'[^a-z0-9]+', '_', prompt.lower())[:40].strip('_') or 'prd'
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = config.OUTPUT_DIR / f'prd_{mode}_{slug}.md'
        n = 1
        while path.exists():
            path = config.OUTPUT_DIR / f'prd_{mode}_{slug}_{n}.md'
            n += 1
        path.write_text(text, encoding='utf-8')

    def generate_prd(self, user_input: str) -> str:
        messages = self._build_messages(user_input)
        result = self._generate_cloud(messages)
        self._save_output(result, user_input, 'rag')
        return result

    def generate_no_rag(self, prompt: str) -> str:
        messages = [
            {'role': 'system', 'content': f"{TEMPLATE_LABEL}\n\nBUAT PRD BERDASARKAN PENGETAHUAN ANDA SENDIRI."},
            {'role': 'user', 'content': prompt},
        ]
        result = self._generate_cloud(messages)
        self._save_output(result, prompt, 'no_rag')
        return result

    def generate_prd_async(self, user_input: str):
        messages = self._build_messages(user_input)
        self._start_cloud_generation(messages)
