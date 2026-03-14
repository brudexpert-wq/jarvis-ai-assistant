"""Configuração do Jarvis Assistant.

Você pode editar essas variáveis para adaptar o comportamento do assistente.
"""

import os

# Idioma a ser utilizado no reconhecimento de voz e na fala (código ISO 639‑1)
LANGUAGE = os.getenv("JARVIS_LANGUAGE", "pt-BR")

# Nome de ativação. O assistente só responde quando o texto da fala começa com este prefixo.
WAKE_WORD = os.getenv("JARVIS_WAKE_WORD", "jarvis").lower()

# Número de recordações a recuperar da memória vetorial
RETRIEVE_K = int(os.getenv("JARVIS_RETRIEVE_K", "3"))

# Método de reconhecimento de voz a ser usado pela biblioteca SpeechRecognition.
# Opções: "whisper", "google", "sphinx". Whisper requer a API da OpenAI.
RECOGNIZER_METHOD = os.getenv("JARVIS_RECOGNIZER_METHOD", "whisper")

# Modelo do LLM usado pelo ChatGPT. Pode ser alterado para outra versão
LLM_MODEL = os.getenv("JARVIS_LLM_MODEL", "gpt-3.5-turbo")

# Mensagem de sistema que define o comportamento do assistente
SYSTEM_PROMPT = os.getenv(
    "JARVIS_SYSTEM_PROMPT",
    "Você é Jarvis, um assistente pessoal inteligente que fala português. "
    "Responda de forma amigável e profissional. Use as funções disponíveis quando forem úteis." ,
)

# Caminho para o banco de dados vetorial (pasta será criada automaticamente)
VECTOR_DB_PATH = os.getenv("JARVIS_VECTOR_DB_PATH", "jarvis_vector_db")

# Caminho para arquivo de memória simples (fallback)
SIMPLE_MEMORY_PATH = os.getenv("JARVIS_SIMPLE_MEMORY_PATH", "jarvis_memory.json")

# Máximo de mensagens simples a manter em memória se o vetor não estiver disponível
SIMPLE_MEMORY_MAX = int(os.getenv("JARVIS_SIMPLE_MEMORY_MAX", "10"))

# API Key da OpenAI: definida via variável de ambiente OPENAI_API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")