# Frontend Blueprint

Documento de mapa entre telas do frontend e APIs do backend.  
Objetivo: colocar cada dado no lugar certo, sem misturar dado bruto, resumo, histórico e análise editorial.

## Princípios

- Dado bruto vai para detalhe e listas.
- Dado resumido vai para cards, hero e KPIs.
- Dado comparativo vai para blocos lado a lado.
- Dado interpretativo do agente vai para uma seção separada.
- API administrativa não entra na experiência principal.

## APIs E Papel

### `GET /api/calendario/proximas`
- Serve a agenda de jogos futuros.
- Entra na home como preview editorial e na tela de calendário como lista principal de próximos jogos.
- Não deve ser usado como fonte de histórico de partidas já encerradas.

### `GET /api/selecoes/{selecao_id}/estatisticas`
- É a API principal da ficha de uma seleção.
- Alimenta KPIs, médias, indicadores percentuais, forma recente e tendências.
- Deve ser o bloco mais importante da tela de seleção.

### `GET /api/partidas/selecao/{selecao_id}`
- Serve o histórico da seleção.
- Entra em listas de partidas, sequência recente e leitura de performance da janela.
- Deve ficar abaixo dos KPIs, como contexto temporal.

### `GET /api/partidas/{partida_id}`
- Serve o detalhe bruto da partida.
- Alimenta placar, status, data, localização, estatísticas da partida e eventos.
- É a fonte da tela de partida individual.

### `GET /api/power-ranking/{selecao_id}`
- Serve contexto de posição e variação no ranking.
- Entra como bloco secundário na ficha da seleção e como apoio no comparador.
- Não deve competir com os KPIs principais.

### `GET /api/h2h/{selecao_a_id}/{selecao_b_id}`
- Serve confronto direto entre duas seleções.
- Entra no comparador e, quando fizer sentido, na tela de partida como contexto.
- É um dado de decisão, não um dado decorativo.

### `GET /api/jogadores/selecao/{selecao_id}`
- Serve elenco e composição da seleção.
- Entra em uma aba de jogadores ou numa seção secundária da ficha da seleção.
- Deve vir depois da visão estatística, nunca antes.

### `GET /api/agente/analise/{partida_id}`
- Serve a leitura editorial da partida.
- Alimenta previsão, narrativa, mercados e bilhetes.
- Deve aparecer só na tela de partida, em bloco separado dos dados crus.

### `POST /api/pipeline`
- Serve execução administrativa do pipeline.
- Não faz parte da navegação pública.
- Se permanecer no frontend, precisa ficar isolado em área restrita.

## Mapa De Telas

### Home
**Função**
- Visão inicial do produto.
- Entrada para navegação e descoberta.

**Blocos**
- Hero institucional com nome do produto e valor central.
- Ações rápidas: selecionar time, abrir calendário, abrir comparador.
- Próximos jogos em destaque.
- Cards-resumo com recortes de seleções em evidência.

**APIs**
- `GET /api/calendario/proximas`
- `GET /api/selecoes/{selecao_id}/estatisticas` para destaques pontuais

**Regra de conteúdo**
- Mostrar poucos dados, bem hierarquizados.
- A home deve orientar navegação, não substituir a ficha da seleção.

### Ficha da Seleção
**Função**
- Tela principal do produto.
- Lugar onde a análise realmente acontece.

**Blocos**
- Cabeçalho com nome, bandeira, grupo e identificação visual.
- KPIs principais.
- Indicadores percentuais.
- Forma recente.
- Tendência e qualidade da janela.
- Histórico de partidas.
- Power ranking.
- Lista de jogadores.

**APIs**
- `GET /api/selecoes/{selecao_id}/estatisticas`
- `GET /api/partidas/selecao/{selecao_id}`
- `GET /api/power-ranking/{selecao_id}`
- `GET /api/jogadores/selecao/{selecao_id}`

**Regra de conteúdo**
- KPIs e indicadores no topo.
- Histórico e elenco abaixo.
- Power ranking como contexto, não como destaque principal.

### Comparador
**Função**
- Comparar duas seleções lado a lado.

**Blocos**
- Seletor A e B.
- Cabeçalho com bandeiras e nomes.
- Forma lado a lado.
- Barras comparativas por categoria.
- Resumo final de quem lidera em mais métricas.
- Confronto direto.
- Ranking contextual.

**APIs**
- `GET /api/selecoes/{selecao_id}/estatisticas` para ambos os lados
- `GET /api/h2h/{selecao_a_id}/{selecao_b_id}`
- `GET /api/power-ranking/{selecao_id}` se quiser reforço contextual

**Regra de conteúdo**
- Não misturar dado estatístico com narrativa.
- O comparador precisa ser objetivo e rápido de ler.

### Calendário
**Função**
- Explorar os próximos jogos.

**Blocos**
- Filtros por data e grupo.
- Lista de partidas futuras.
- Estado de encerrado/agendado.

**APIs**
- `GET /api/calendario/proximas`

**Regra de conteúdo**
- Se a tela for “agenda”, manter o foco em próximos jogos.
- Se no futuro houver calendário completo, criar um endpoint próprio para isso.

### Detalhe Da Partida
**Função**
- Exibir partida individual com leitura analítica.

**Blocos**
- Cabeçalho da partida.
- Placar e status.
- Estatísticas da partida.
- Eventos.
- Confronto direto.
- Análise do agente.
- Bilhetes.

**APIs**
- `GET /api/partidas/{partida_id}`
- `GET /api/agente/analise/{partida_id}`
- `GET /api/h2h/{selecao_a_id}/{selecao_b_id}` se os times estiverem disponíveis

**Regra de conteúdo**
- Dados da partida primeiro.
- Leitura do agente depois.
- Bilhetes sempre separados dos números crus.

### Pipeline
**Função**
- Operação técnica e administrativa.

**Blocos**
- Status da última execução.
- Log recente.
- Histórico de execuções.
- Botão de disparo, se mantido.

**APIs**
- `POST /api/pipeline`
- Fonte de dados do status pode vir de uma API futura ou de um endpoint administrativo próprio.

**Regra de conteúdo**
- Isso não é parte do produto principal.
- Deve ter aparência técnica, discreta e isolada.

## Ordem De Prioridade Visual

1. Identidade da seleção ou partida.
2. KPIs e leitura principal.
3. Contexto de janela e forma.
4. Comparação.
5. Histórico.
6. Narrativa do agente.

## Regras De Layout

- Sem menu lateral.
- Navegação compacta e discreta.
- Fundo grafite na versão escura.
- Fundo off-white técnico na versão clara.
- Roxo e magenta só como acento fino.
- Tipografia alternativa, sem aparência padrão de IA.
- O visual deve parecer institucional esportivo, com ritmo e sobriedade.

## Observação De Arquitetura

Hoje o backend já tem rotas suficientes para o núcleo analítico do produto.  
O frontend novo deve apenas organizar essas rotas por contexto de uso:

- descoberta
- análise da seleção
- comparação
- detalhe da partida
- operação técnica

Se uma informação não ajuda uma dessas cinco intenções, ela provavelmente está no lugar errado.
