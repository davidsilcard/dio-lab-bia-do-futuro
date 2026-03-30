# BIA Futuro

Protótipo de assistente financeiro para o desafio `dio-lab-bia-do-futuro`, com foco em orientação prudente, transparência e respostas ancoradas nos dados mockados do repositório.

## O que a aplicação faz

- analisa gastos por categoria a partir de `data/transacoes.csv`;
- acompanha a meta de reserva de emergência com base em `data/perfil_investidor.json`;
- recupera contexto de atendimentos anteriores;
- recomenda produtos aderentes ao perfil e ao objetivo principal do cliente;
- exibe insights proativos logo na abertura da aplicação;
- mostra evidência da resposta e próximo passo sugerido no chat;
- recusa perguntas sem base suficiente ou fora do escopo financeiro.

## Estrutura

- `src/app.py`: interface Streamlit
- `src/agent.py`: regras do agente e respostas
- `src/knowledge_base.py`: leitura e agregação dos dados
- `docs/`: documentação do desafio já preenchida

## Como executar

```bash
uv venv
uv pip install -r src/requirements.txt
uv run streamlit run src/app.py
```

## Perguntas para demonstrar

- `Quanto gastei com alimentação?`
- `Como está minha reserva de emergência?`
- `Qual produto combina com meu perfil?`
- `Me dê um resumo financeiro do mês.`

## Segurança

O protótipo não depende de API externa e só responde com base nos arquivos da pasta `data/`. Cada resposta exibe as fontes usadas.
