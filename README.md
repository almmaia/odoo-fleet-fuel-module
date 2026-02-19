# Controle de Combustivel para Odoo Fleet (Odoo Community)

Modulo customizado para registrar abastecimentos e controlar estoque de combustivel no Odoo Fleet.

## Objetivo
- Registrar abastecimentos por equipamento/placa (fleet.vehicle).
- Calcular custo por abastecimento automaticamente.
- Controlar estoque de um tanque principal (6000L por padrao).
- Separar permissoes por perfil: Motorista, Analista e Administrador.

## Funcionalidades
- Cadastro de abastecimentos com:
  - equipamento/placa
  - data/hora
  - horimetro/odometro
  - litros
  - valor por litro
  - total calculado
  - usuario responsavel
  - motorista
- Metricas por veiculo:
  - KM rodado
  - consumo (KM/L)
  - custo por KM
- Controle de estoque em tanque:
  - entradas aumentam estoque
  - abastecimentos reduzem estoque
  - bloqueio para saldo insuficiente
  - bloqueio para exceder capacidade
- Relatorios:
  - visao pivot
  - visao graph
- Estrutura de integracao para recebimento de compra em `fuel.stock.move`:
  - `integration_source`
  - `source_document`
  - `source_partner`
  - `create_from_purchase_receipt(...)`

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

## Executar no WSL
### Pre-requisitos
- Ubuntu WSL
- Python 3.10+
- PostgreSQL
- Odoo 19.0 clonado em `~/odoo`

### Passos
1. Ativar ambiente:
```bash
cd ~/odoo
source .venv/bin/activate
```

2. Subir PostgreSQL:
```bash
sudo pg_ctlcluster 14 main start --skip-systemctl-redirect
```

3. Rodar Odoo com este addon:
```bash
./odoo-bin -d odoo19_dev -r alan -w alan --db_host=127.0.0.1 --db_port=5433 --addons-path=addons,/mnt/c/Users/Lenovo/Downloads/odoo-fleet-fuel-module/custom_addons
```

4. Abrir no navegador:
- `http://localhost:8069`

## Executar com Docker
### Opcao 1: docker run
```bash
docker run -d --name odoo19-db \
  -e POSTGRES_DB=postgres \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  postgres:14

docker run -d --name odoo19-web -p 8069:8069 \
  --link odoo19-db:db \
  -v /c/Users/Lenovo/Downloads/odoo-fleet-fuel-module/custom_addons:/mnt/extra-addons \
  -e HOST=db -e USER=odoo -e PASSWORD=odoo \
  odoo:19.0
```

### Opcao 2: docker-compose
```yaml
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo

  web:
    image: odoo:19.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      HOST: db
      USER: odoo
      PASSWORD: odoo
    volumes:
      - ./custom_addons:/mnt/extra-addons
```

Subida:
```bash
docker compose up -d
```

## Instalar o modulo no Odoo
1. Acesse `Apps`.
2. Clique em `Update Apps List`.
3. Busque `Controle de Combustivel`.
4. Clique em `Install` (ou `Upgrade`).

## Roteiro de teste completo
1. Acesse `Combustivel > Tanque` e confirme o tanque principal (6000L).
2. Em `Combustivel > Entradas/Ajustes`, crie uma entrada de estoque.
3. Verifique no tanque se o estoque aumentou.
4. Em `Combustivel > Abastecimentos`, crie um abastecimento com veiculo, odometro, litros e valor/litro.
5. Verifique se o total foi calculado automaticamente.
6. Verifique se o estoque do tanque foi reduzido.
7. Crie um segundo abastecimento no mesmo veiculo e confira `KM Rodado`, `KM/L` e `Custo por KM`.
8. Tente abastecer acima do saldo do tanque e valide o bloqueio.
9. Acesse `Combustivel > Relatorios` e valide `Pivot` e `Graph`.
10. Teste permissoes por perfil:
   - Motorista: registra abastecimento, sem ajuste manual de estoque.
   - Analista: visualiza abastecimentos, relatorios e movimentacoes.
   - Admin: acesso total.
