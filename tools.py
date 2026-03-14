"""Funções externas que o assistente pode executar.

Cada função precisa ser registrada na lista FUNCTIONS com um esquema JSON de parâmetros para que
o modelo da OpenAI possa reconhecê‑la.  Ao adicionar novas funções aqui, certifique‑se de atualizar
a lista FUNCTIONS mais abaixo.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from . import config


def get_current_time() -> Dict[str, str]:
    """Retorna a hora atual como string (formato 24h) em português."""
    now = datetime.now()
    # Formatar em português (dia/mês/ano e hora:min:sec)
    return {"time": now.strftime("%d/%m/%Y %H:%M:%S")}


def turn_on_light(room: str) -> Dict[str, str]:
    """Exemplo de função para acender uma luz em um cômodo.  
    Substitua esta implementação pela chamada real ao Home Assistant ou outro hub.
    """
    # Aqui você poderia chamar a API do Home Assistant ou enviar comando via MQTT.
    # Por enquanto, apenas retornamos uma mensagem simulada.
    return {"status": f"Luz do cômodo '{room}' acesa."}


def search_web(query: str) -> Dict[str, str]:
    """Pesquisa simples na web (placeholder).  
    Idealmente usaria uma API de busca (como SerpAPI ou DuckDuckGo).  Aqui retornamos uma mensagem
    indicando que a busca foi executada.
    """
    return {"result": f"(Pesquisa simulada) Resultados para '{query}'"}


def get_tools() -> Dict[str, Any]:
    """Mapeia nomes de funções para objetos chamáveis."""
    return {
        "get_current_time": get_current_time,
        "turn_on_light": turn_on_light,
        "search_web": search_web,
    }


# Definições de funções para a API da OpenAI
FUNCTION_DEFINITIONS = [
    {
        "name": "get_current_time",
        "description": "Obtém a data e hora atual.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "turn_on_light",
        "description": "Acende a luz de um cômodo específico.",
        "parameters": {
            "type": "object",
            "properties": {
                "room": {
                    "type": "string",
                    "description": "Nome do cômodo cuja luz deve ser acesa."
                }
            },
            "required": ["room"],
        },
    },
    {
        "name": "search_web",
        "description": "Executa uma pesquisa rápida na web (placeholder).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termo de pesquisa."
                }
            },
            "required": ["query"],
        },
    },
]