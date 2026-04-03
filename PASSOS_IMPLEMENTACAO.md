# Guia de Implementação Deep-Work

Este guia detalha o passo-a-passo da implementação do sistema de agente autônomo Deep-Work.

## Passo 1: Configuração do Projeto e Dependências
- **Inicialização**: Criado um ambiente Python 3.12.
- **Dependências**: Instalado `pinecone-client`, `langchain-pinecone`, `langchain-openai`, `langgraph`, `playwright`, e `pyautogui`.
- **Ambiente**: Configurado `.env` com as chaves da OpenAI e Pinecone.

## Passo 2: Memória Vetorial com Pinecone (`src/memory/pinecone_manager.py`)
- **Integração**: Implementada a classe `MemoryManager` usando o Pinecone Python SDK v3+.
- **Gerenciamento de Índice**: Adicionada lógica para criar automaticamente um índice serverless com dimensão 1536 (embeddings da OpenAI) e métrica de cosseno.
- **Suporte RAG**: Implementados `aadd_memory` e `asearch_memory` para armazenar e recuperar contextos episódicos/semânticos.

## Passo 3: Desenvolvimento de Ferramentas (`src/tools/`)
- **Automação de Navegador**: Desenvolvido `BrowserTools` usando Playwright, incluindo persistência de sessão (`storage_state`) e resumo de página.
- **Automação de OS**: Desenvolvido `OSTools` usando PyAutoGUI com interação baseada em coordenadas e mock para ambientes headless.

## Passo 4: Núcleo do Agente (`src/agents/`)
- **Planner (Planejador)**: Criado um planejador baseado em GPT-4o que decompõe objetivos em objetos estruturados `Task`.
- **Actor (Ator)**: Construído um mecanismo de despacho para executar tarefas usando as ferramentas de Navegador ou OS.
- **Validator (Validador)**: Implementado um validador com capacidade de visão (GPT-4o) para verificar resultados de tarefas usando capturas de tela e resumos de página.
- **Workflow Synthesizer**: Adicionado um componente para salvar sequências bem-sucedidas de tarefas como workflows reutilizáveis no Pinecone.

## Passo 5: Orquestração com LangGraph (`src/agents/orchestrator.py`)
- **Gerenciamento de Estado**: Definido um `AgentState` para rastrear o objetivo, plano, resultados e tentativas.
- **Construção do Grafo**: Construído um fluxo de trabalho LangGraph com nós para planejamento, execução, validação e finalização.
- **Auto-Correção**: Implementadas bordas condicionais para tentativas e re-planejamento dinâmico em caso de falha.

## Passo 6: Agendamento e Interação (`src/agents/scheduler.py` e `main.py`)
- **Scheduler (Agendador)**: Desenvolvido um `TaskScheduler` para lidar com a execução de objetivos únicos atrasados e periódicos.
- **CLI**: Implementado um loop interativo assíncrono em `main.py` usando `asyncio.to_thread` para entrada de usuário não bloqueante.

## Passo 7: Testes e Verificação (`tests/`)
- **Cobertura**: Desenvolvido um conjunto abrangente de 31 testes cobrindo todos os componentes, alcançando 91% de cobertura.
- **Validação**: Verificado o sistema em um ambiente Dockerizado com Xvfb.
