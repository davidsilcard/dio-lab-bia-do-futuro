# Base de Conhecimento

## Dados Utilizados

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Recuperar temas recentes e contexto de interações anteriores |
| `perfil_investidor.json` | JSON | Identificar perfil, renda, patrimônio, objetivo principal e metas |
| `produtos_financeiros.json` | JSON | Filtrar produtos aderentes ao objetivo e ao nível de risco |
| `transacoes.csv` | CSV | Calcular gastos por categoria, despesas totais e saldo mensal estimado |

---

## Adaptações nos Dados

Não alterei os arquivos originais do desafio. Em vez disso, centralizei a leitura e o processamento na classe `KnowledgeBase`, que transforma os arquivos em estruturas consultáveis e gera indicadores derivados, como:

- saldo mensal estimado;
- ranking de gastos por categoria;
- valor faltante para completar a reserva de emergência;
- shortlist de produtos recomendados.

---

## Estratégia de Integração

### Como os dados são carregados?
Os arquivos são carregados localmente no início da aplicação. A classe `KnowledgeBase` lê `JSON` e `CSV` diretamente da pasta `data/`, sem dependência de banco de dados ou API externa.

### Como os dados são usados no prompt?
Os dados não são despejados integralmente em um prompt longo. Em vez disso, a aplicação aplica regras de intenção e consulta a base dinamicamente, montando apenas o contexto necessário para cada resposta. Essa abordagem reduz custo, simplifica o protótipo e melhora a segurança contra alucinação.

---

## Exemplo de Contexto Montado

```text
Cliente: João Silva
Perfil: moderado
Renda mensal: R$ 5.000,00
Patrimônio: R$ 15.000,00
Objetivo principal: construir reserva de emergência
Reserva atual: R$ 10.000,00
Saldo mensal estimado: R$ 2.511,10

Principais gastos:
- moradia: R$ 1.380,00
- alimentação: R$ 570,00
- transporte: R$ 295,00
```
