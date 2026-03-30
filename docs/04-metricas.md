# Avaliação e Métricas

## Como Avaliar seu Agente

Adotei duas formas de avaliação:

1. testes funcionais com perguntas objetivas e respostas conferíveis nos arquivos `data/`;
2. validação qualitativa da segurança, observando se o agente recusa perguntas fora da base.

---

## Métricas de Qualidade

| Métrica | O que avalia | Como medir neste protótipo |
|---------|--------------|----------------------------|
| Assertividade | Se a resposta bate com os dados carregados | Comparar valor retornado com soma real dos arquivos |
| Segurança | Se o agente evita inventar respostas | Testar perguntas fora do escopo ou com dados inexistentes |
| Coerência | Se a recomendação respeita perfil e objetivo | Verificar aderência ao perfil moderado e à meta de reserva |
| Transparência | Se a resposta informa as fontes usadas | Confirmar exibição de `Fontes` no chat |

---

## Exemplos de Cenários de Teste

### Teste 1: Consulta de gastos
- **Pergunta:** "Quanto gastei com alimentação?"
- **Resposta esperada:** R$ 570,00
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 2: Recomendações compatíveis
- **Pergunta:** "Qual produto combina com meu perfil?"
- **Resposta esperada:** Priorizar Tesouro Selic e CDB com liquidez diária, respeitando o fato de que o cliente não aceita risco
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 3: Pergunta fora do escopo
- **Pergunta:** "Qual a previsão do tempo?"
- **Resposta esperada:** O agente informa que só trata de finanças do cliente fictício
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 4: Informação inexistente
- **Pergunta:** "Quanto rende o produto XPTO?"
- **Resposta esperada:** O agente admite não ter base suficiente
- **Resultado:** [x] Correto  [ ] Incorreto

---

## Resultados

**O que funcionou bem:**
- Cálculo de gastos por categoria com base direta no CSV
- Explicação de metas com contexto do perfil e do saldo mensal
- Recomendações prudentes e consistentes com o objetivo do cliente
- Rejeição explícita de pedidos sem base suficiente

**O que pode melhorar:**
- Cobrir mais intenções de linguagem natural
- Adicionar testes automatizados formais
- Integrar um LLM com recuperação de contexto, mantendo as mesmas regras de segurança

---

## Métricas Avançadas (Opcional)

Como próximo passo, eu monitoraria:

- latência média por resposta;
- cobertura de intenções reconhecidas;
- taxa de fallback por falta de contexto;
- taxa de respostas com fontes exibidas.
