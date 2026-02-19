# Controle de Combustivel para Odoo Fleet (Odoo Community)

Modulo customizado para registrar abastecimentos e controlar estoque de combustivel no Odoo Fleet.

## Objetivo do modulo
- Registrar abastecimentos por equipamento/placa (fleet.vehicle).
- Calcular custo por abastecimento automaticamente.
- Controlar estoque de um tanque principal (6000L por padrao).
- Separar permissoes por perfil: Motorista, Analista e Administrador.

## Escopo atendido do teste
### 1) Abastecimentos
- Integracao com equipamentos/placas do Odoo Fleet.
- Campos implementados: equipamento/placa, data/hora, horimetro/odometro, litros, valor por litro, total calculado, usuario responsavel e motorista.
- Metricas calculadas: KM rodado, consumo (KM/L) e custo por KM.

### 2) Estoque de combustivel (tanque 6000L)
- Tanque principal criado por dado inicial.
- Entradas aumentam estoque.
- Abastecimentos reduzem estoque.
- Exibicao de estoque atual no cadastro do tanque.
- Validacoes para impedir saldo negativo e excesso de capacidade.

### 3) Permissoes
- Motorista: registra abastecimentos e consulta tanque.
- Analista: visualiza abastecimentos, relatorios e movimentacoes de estoque.
- Administrador Combustivel: acesso total ao modulo.

## Diferenciais implementados
- Relatorios com visualizacao `pivot` e `graph` para analise de litros e custo por periodo/veiculo.
- Search view com filtros e agrupamentos para analise operacional.
- Trilhas de integracao em entradas de estoque:
  - campos de origem (`integration_source`, `source_document`, `source_partner`)
  - metodo `create_from_purchase_receipt(...)` em `fuel.stock.move` para integrar recebimentos de compra.
- Regras de consistencia de estoque em `create`, `write` e `unlink` dos abastecimentos.

## Estrutura
- `custom_addons/controle_combustivel/__manifest__.py`
- `custom_addons/controle_combustivel/models/fuel_log.py`
- `custom_addons/controle_combustivel/models/fuel_tank.py`
- `custom_addons/controle_combustivel/models/fuel_stock_move.py`
- `custom_addons/controle_combustivel/security/security.xml`
- `custom_addons/controle_combustivel/security/ir.model.access.csv`
- `custom_addons/controle_combustivel/views/fuel_log_views.xml`
- `custom_addons/controle_combustivel/views/fuel_tank_views.xml`
- `custom_addons/controle_combustivel/views/fuel_stock_move_views.xml`
- `custom_addons/controle_combustivel/data/fuel_tank_data.xml`

## Como instalar
1. Copie `custom_addons/controle_combustivel` para o `addons_path` do Odoo.
2. Atualize a lista de aplicativos.
3. Instale/atualize o modulo `Controle de Combustivel`.

## Roteiro rapido de teste (recrutador)
1. Acesse `Combustivel > Tanque` e confirme o tanque principal de 6000L.
2. Como Admin, crie uma `Entrada` em `Combustivel > Entradas/Ajustes`.
3. Registre um abastecimento em `Combustivel > Abastecimentos`.
4. Verifique reducao de estoque do tanque.
5. Tente abastecer acima do saldo para validar bloqueio.
6. Abra `Combustivel > Relatorios` e confira `Pivot` e `Graph`.
7. Teste perfis (Motorista, Analista, Admin) conforme regras de acesso.

## Dificuldades e melhorias futuras
- Dificuldade principal: manter consistencia de estoque em alteracoes de abastecimento sem perder historico.
- Melhorias futuras:
  - Integracao completa com `purchase`/`stock` para entrada automatica por recebimento validado.
  - Dashboard gerencial por periodo, veiculo e motorista.
  - Alertas de estoque minimo.

## Proposta tecnica de integracao NF-e / NFS-e
- NF-e (entrada de combustivel):
  - capturar XML autorizado
  - extrair fornecedor, numero/chave, produto combustivel, quantidade e valor unitario
  - converter em movimento `fuel.stock.move` com `integration_source = purchase_receipt`
  - armazenar chave NF-e no campo de documento de origem
- NFS-e (servicos relacionados):
  - registrar custos de servicos (frete, manutencao, terceiros) vinculados ao centro de custo/frota
  - consolidar em relatorio financeiro da frota

## Retorno tecnico de ambiente (resumo)
- Plataforma-alvo: Odoo 19 Community.
- Estrutura modular em `models/views/security/data`.
- Regras de negocio implementadas com ORM e validacoes.
- Views com foco operacional (tree/form) e analitico (pivot/graph).

## Modelo de e-mail de envio
Assunto: `VAGA DEV PYTHON - SEU NOME`

Corpo sugerido:

Prezados,

Segue minha entrega do Teste Pratico para a vaga de Desenvolvedor(a) Full Stack Python Junior.

- Repositorio: `<cole_o_link_do_repositorio>`
- Modulo: `controle_combustivel`
- Versao: `1.3.0`

Resumo da entrega:
- Ambiente Odoo Community configurado.
- Modulo com abastecimentos, controle de tanque e permissoes por perfil.
- Diferenciais: relatorios (pivot/graph) e estrutura de integracao de recebimento de compras.
- Proposta tecnica para integracao NF-e/NFS-e descrita no README.

Fico a disposicao para esclarecimentos.

Atenciosamente,
`SEU NOME`

## Observacao de prazo
No enunciado aparecem duas datas de prazo: `24/01/2026` e `15/02/2026`. Ambas sao anteriores a `19/02/2026`.
