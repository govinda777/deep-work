# Documentação Técnica Deep-Work

## 1. Visão Geral da Arquitetura
O sistema Deep-Work segue uma arquitetura **Planner-Actor-Validator** orquestrada usando **LangGraph**. Isso permite um agente autônomo robusto e auto-corretivo, capaz de automação web e de sistema operacional (OS).

### 1.1 O Orquestrador (`src/agents/orchestrator.py`)
O Orquestrador gerencia o estado e o ciclo de vida do agente. Ele define um grafo com três nós principais:
- **Plan (Planejar)**: Decompõe um objetivo em uma sequência de tarefas.
- **Execute (Executar)**: Realiza uma única tarefa usando o Actor.
- **Validate (Validar)**: Verifica se o resultado esperado da tarefa foi alcançado.

### 1.2 Gerenciamento de Memória com Pinecone (`src/memory/pinecone_manager.py`)
O Deep-Work utiliza o **Pinecone** como um banco de dados vetorial para gerenciar memória episódica e semântica.
- **Memória Episódica**: Armazena execuções de tarefas individuais, resultados e planos.
- **Memória Semântica**: Permite que o agente recupere experiências passadas relevantes usando embeddings da OpenAI para informar o planejamento atual (RAG).
- **Suporte Assíncrono**: Implementa `aadd_memory` e `asearch_memory` para I/O eficiente e não bloqueante.

## 2. Componentes Principais

### 2.1 Planner (`src/agents/planner.py`)
Usa o GPT-4o para gerar um `Plan` estruturado (uma lista de objetos `Task`). O planejador recebe um esquema detalhado de todas as ações disponíveis de Browser e OS para garantir a geração de planos de alta fidelidade.

### 2.2 Actor (`src/agents/actor.py`)
O braço de execução do sistema. Ele despacha tarefas para `BrowserTools` ou `OSTools` com base no `tool_type` da tarefa.

### 2.3 Validator (`src/agents/validator.py`)
Um componente com capacidade de visão que usa o GPT-4o para comparar o estado atual do sistema (resumo da página e/ou captura de tela) com o `expected_outcome` da tarefa.

### 2.4 Workflow Synthesizer (`src/agents/recorder.py`)
Após a conclusão bem-sucedida de um objetivo, este componente extrai a sequência de tarefas e a armazena no Pinecone como um "Workflow". O Orquestrador verifica esses workflows ao iniciar novos objetivos para reutilizar sequências comprovadas.

### 2.5 Task Scheduler (`src/agents/scheduler.py`)
Permite operações autônomas em segundo plano. Suporta:
- **Execução Única**: Executa um objetivo uma vez após um atraso especificado.
- **Execução Periódica**: Executa repetidamente um objetivo em um intervalo fixo.

## 3. Ferramentas e Integração

### 3.1 Automação de Navegador (`src/tools/browser_tools.py`)
Alimentado pelo **Playwright**.
- **Persistência de Sessão**: Salva e carrega o `storage_state` (cookies, armazenamento local) em `session_state.json`, permitindo que o agente permaneça logado em sites.
- **Resumo de Página**: Gera uma representação baseada em texto de elementos interativos do DOM para processamento eficiente pelo LLM.

### 3.2 Automação de OS (`src/tools/os_tools.py`)
Alimentado pelo **PyAutoGUI**.
- **Interação baseada em Coordenadas**: Suporta cliques, cliques duplos e arrastos em pixels específicos (x, y).
- **Compatibilidade Headless**: Inclui mocks para ambientes sem um display físico, suportando CI/CD e execução Dockerizada com Xvfb.

## 4. Configuração e Implantação

### 4.1 Variáveis de Ambiente
As seguintes chaves são necessárias em um arquivo `.env`:
- `OPENAI_API_KEY`: Para raciocínio do LLM e embeddings.
- `PINECONE_API_KEY`: For armazenamento de memória vetorial.
- `PINECONE_INDEX_NAME`: O nome do seu índice Pinecone (ex: `deep-work-memory`).
- `DISPLAY`: Definir como `:99` ao rodar no Docker com Xvfb.

### 4.2 Execução Dockerizada
O Deep-Work foi projetado para rodar em um container para garantir um ambiente isolado.
```bash
docker-compose up --build
```
Isso inicia um display virtual **Xvfb** em `:99`, fornecendo um ambiente GUI para o Playwright e PyAutoGUI.

### 4.3 Testes e Cobertura
O Deep-Work mantém um alto padrão de confiabilidade com mais de 90% de cobertura de testes.
- **Executar Testes**: `PYTHONPATH=. python3 -m unittest discover tests`
- **Verificar Cobertura**:
  ```bash
  pip install coverage
  PYTHONPATH=. coverage run -m unittest discover tests
  coverage report
  ```

## 5. Stack Técnica
- **Linguagem**: Python 3.12
- **Orquestração**: LangGraph
- **Memória**: Pinecone (Vector DB)
- **LLMs**: GPT-4o (Raciocínio, Visão, Planejamento)
- **Automação**: Playwright (Navegador), PyAutoGUI (OS)
- **Ambiente**: Docker, Xvfb
