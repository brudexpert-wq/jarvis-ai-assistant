# Jarvis Voice Assistant

Este projeto implementa um assistente pessoal no estilo **Jarvis** usando Python.  Ele combina reconhecimento de fala, um modelo de linguagem (ChatGPT ou Llama), memória persistente baseada em vetores e ferramentas para executar ações (por exemplo, controlar dispositivos domésticos, obter a hora atual).  O código é modular para permitir que você substitua componentes (por exemplo, usar um modelo local em vez da API da OpenAI) e oferece suporte a português.

## Principais recursos

* **Reconhecimento de fala (STT)**: Usa a biblioteca `speech_recognition` para ouvir um microfone e transcrever comandos de voz.  Por padrão utiliza o serviço Whisper da API da OpenAI; é possível mudar para Google ou Vosk configurando `recognizer_method` em `config.py`.
* **Síntese de voz (TTS)**: Usa `pyttsx3` para falar as respostas de forma offline.  Se preferir vozes mais naturais, substitua por `piper` ou outro serviço de TTS.
* **Modelo de linguagem (LLM)**: Usa a API da OpenAI para ChatGPT (função `openai.ChatCompletion.create`).  Você pode apontar para um modelo local (como Llama 3 ou Mistral) modificando `assistant.py`.
* **Memória persistente**: Armazena conversas em um banco vetorial usando `chromadb`, permitindo que o assistente lembre de interações anteriores e recupere trechos relevantes para novos prompts.  Se `chromadb` não estiver disponível, o código recorre a uma memória simples em arquivo.
* **Ferramentas (function calling)**: Define funções que o LLM pode invocar (por exemplo, `get_current_time`, `turn_on_light`).  O ChatGPT analisa as intenções do usuário, decide se deve chamar uma função e, se o fizer, o resultado é passado de volta ao LLM para gerar a resposta final.

## Requisitos

Instale os pacotes necessários em um ambiente virtual Python (recomenda‑se Python 3.10 ou superior):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

O arquivo `requirements.txt` inclui dependências como `speechrecognition`, `pyttsx3`, `openai`, `chromadb` e `langchain`.  Alguns pacotes (por exemplo, `pyaudio`) podem exigir bibliotecas de sistema — consulte a documentação da biblioteca para instruções de instalação.

### Configuração da chave API

Para usar o ChatGPT, defina a variável de ambiente `OPENAI_API_KEY` com sua chave de API:

```bash
export OPENAI_API_KEY="sua-chave-aqui"
```

### Execução

Depois de instalar as dependências e definir a chave da API, execute o assistente:

```bash
python -m jarvis_assistant.main
```

O assistente ficará em modo de escuta.  Fale “Jarvis” seguido do comando em português (por exemplo, “Jarvis, que horas são?”).  O script detecta a palavra de ativação, transcreve o áudio, envia a consulta ao LLM, executa funções se necessário e responde em voz alta.

## Personalização

* **Ferramentas adicionais**: Adicione novas funções em `jarvis_assistant/tools.py` e inclua descrições/parametros na lista `FUNCTIONS` para que o LLM possa usá‑las.
* **Memória**: Ajuste a classe `VectorMemory` em `jarvis_assistant/memory.py` para utilizar outro banco vetorial (por exemplo, Qdrant).  Você também pode modificar o parâmetro `k` em `retrieve` para retornar mais ou menos lembranças.
* **Wake word**: O código atualmente usa um prefixo de comando “Jarvis” para detectar a intenção.  Para um wake word sempre ativo, integre `snowboy` ou `porcupine`.
* **Voz**: Configure a voz em `pyttsx3` via `engine.setProperty('voice', ...)` para usar vozes em português.  Consulte a documentação do `pyttsx3` para listar vozes disponíveis no seu sistema.

## Aviso

Este projeto fornece uma base para você desenvolver seu próprio Jarvis.  Algumas bibliotecas podem não funcionar em todos os sistemas ou podem exigir configurações adicionais (por exemplo, drivers de áudio).  Adapte o código conforme necessário e consulte a documentação oficial das bibliotecas envolvidas para suporte.
