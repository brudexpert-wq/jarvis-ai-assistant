"""Ponto de entrada do Jarvis Voice Assistant.

Este módulo implementa um loop de conversação que escuta o microfone, reconhece comandos de voz,
envia-os a um modelo de linguagem (ChatGPT) com memória e funções disponíveis, executa chamadas
de função quando apropriado e responde ao usuário utilizando síntese de voz.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from typing import List, Dict, Optional, Any

import openai  # type: ignore
import speech_recognition as sr  # type: ignore
import pyttsx3  # type: ignore

from . import config
from .memory import get_memory, Message
from .tools import get_tools, FUNCTION_DEFINITIONS


def initialize_tts() -> pyttsx3.Engine:
    engine = pyttsx3.init()
    # Ajustar voz para português, se disponível
    voices = engine.getProperty('voices')
    for voice in voices:
        # Dependendo do sistema, as vozes podem ter nomes diferentes
        if 'brazil' in voice.name.lower() or 'português' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    return engine


def speak(engine: pyttsx3.Engine, text: str) -> None:
    """Faz o assistente falar uma string através do TTS."""
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()


def listen(recognizer: sr.Recognizer, microphone: sr.Microphone) -> Optional[str]:
    """Escuta o microfone e retorna a transcrição de voz em texto.
    Pode retornar None se a transcrição falhar."""
    with microphone as source:
        print("Aguardando fala...")
        audio = recognizer.listen(source, phrase_time_limit=10)
    try:
        method = config.RECOGNIZER_METHOD.lower()
        if method == "whisper" and hasattr(recognizer, 'recognize_whisper_api'):
            # Necessita chave da API da OpenAI
            transcript = recognizer.recognize_whisper_api(
                audio, api_key=config.OPENAI_API_KEY, language=config.LANGUAGE
            )
        elif method == "google":
            transcript = recognizer.recognize_google(audio, language=config.LANGUAGE)
        elif method == "sphinx":
            transcript = recognizer.recognize_sphinx(audio, language=config.LANGUAGE)
        else:
            transcript = recognizer.recognize_google(audio, language=config.LANGUAGE)
        return transcript.lower()
    except Exception as e:
        print(f"Erro ao reconhecer fala: {e}")
        return None


def prepare_messages(memory: Any, tools: Dict[str, Any], user_query: str) -> List[Dict[str, str]]:
    """Cria a lista de mensagens (histórico + sistema + contexto) para enviar ao LLM."""
    messages: List[Dict[str, str]] = []
    # Mensagem de sistema
    messages.append({"role": "system", "content": config.SYSTEM_PROMPT})
    # Recuperar memórias relevantes (se aplicável)
    try:
        context_messages = memory.retrieve(user_query, k=config.RETRIEVE_K)
        for m in context_messages:
            messages.append({"role": m.role, "content": m.content})
    except Exception:
        pass
    # Adicionar a consulta atual
    messages.append({"role": "user", "content": user_query})
    return messages


def call_llm(messages: List[Dict[str, str]], functions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Envia mensagens e definição de funções ao LLM e retorna a resposta bruta."""
    response = openai.ChatCompletion.create(
        model=config.LLM_MODEL,
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=0.7,
    )
    return response


def process_response(
    response: Dict[str, Any], tools: Dict[str, Any], messages: List[Dict[str, str]], memory: Any
) -> str:
    """Processa a resposta do LLM.  Se houver chamada de função, executa a função e faz nova chamada.
    Retorna o texto final a ser falado."""
    choice = response["choices"][0]["message"]
    # Verificar se o modelo solicitou uma chamada de função
    if "function_call" in choice:
        fc = choice["function_call"]
        func_name = fc.get("name")
        arguments_str = fc.get("arguments") or {}
        try:
            args = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
        except json.JSONDecodeError:
            args = {}
        # Executar a função correspondente
        tool = tools.get(func_name)
        if tool:
            try:
                result = tool(**args)
            except Exception as e:
                result = {"error": str(e)}
        else:
            result = {"error": f"Função '{func_name}' não encontrada."}
        # Adicionar a chamada de função e resultado ao histórico
        messages.append(
            {
                "role": "assistant",
                "content": None,
                "function_call": {"name": func_name, "arguments": json.dumps(args)},
            }
        )
        messages.append({"role": "function", "name": func_name, "content": json.dumps(result)})
        # Nova chamada ao LLM com a saída da função
        second_response = openai.ChatCompletion.create(
            model=config.LLM_MODEL,
            messages=messages,
            temperature=0.7,
        )
        final_message = second_response["choices"][0]["message"]
        content = final_message.get("content", "")
        # Salvar na memória
        memory.add(Message(role="assistant", content=content))
        return content
    else:
        # Resposta direta
        content = choice.get("content", "")
        # Salvar na memória
        memory.add(Message(role="assistant", content=content))
        return content


def run_assistant() -> None:
    """Loop principal do assistente Jarvis."""
    if not config.OPENAI_API_KEY:
        print("Erro: defina a variável de ambiente OPENAI_API_KEY com sua chave da OpenAI.")
        return
    openai.api_key = config.OPENAI_API_KEY
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    tts_engine = initialize_tts()
    memory = get_memory()
    tools = get_tools()
    print("Jarvis iniciado. Diga 'Jarvis' seguido de um comando.")
    while True:
        try:
            transcript = listen(recognizer, microphone)
            if not transcript:
                continue
            # Checar wake word
            if not transcript.strip().startswith(config.WAKE_WORD):
                continue
            # Remover wake word
            user_query = transcript[len(config.WAKE_WORD):].strip().lstrip(',.?:!;')
            # Adicionar à memória como mensagem de usuário
            memory.add(Message(role="user", content=user_query))
            # Preparar mensagens com contexto
            messages = prepare_messages(memory, tools, user_query)
            # Chamar LLM
            response = call_llm(messages, FUNCTION_DEFINITIONS)
            # Processar resposta
            reply = process_response(response, tools, messages, memory)
            # Falar resposta
            if reply:
                speak(tts_engine, reply)
        except KeyboardInterrupt:
            print("\nAssistente encerrado.")
            break
        except Exception as e:
            print("Erro no loop principal:", e)
            traceback.print_exc()
            speak(tts_engine, "Desculpe, ocorreu um erro.")


if __name__ == "__main__":
    run_assistant()