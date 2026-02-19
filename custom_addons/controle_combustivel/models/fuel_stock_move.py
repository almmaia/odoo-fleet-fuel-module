from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FuelStockMove(models.Model):
    _name = "fuel.stock.move"
    _description = "Movimentacao do Tanque"
    _order = "date desc, id desc"

    tank_id = fields.Many2one(
        "fuel.tank",
        string="Tanque",
        required=True,
        default=lambda self: self._default_tank_id(),
    )
    date = fields.Datetime(string="Data/Hora", required=True, default=fields.Datetime.now)

    move_type = fields.Selection(
        [("in", "Entrada"), ("adjust", "Ajuste")],
        string="Tipo",
        required=True,
        default="in",
    )

    liters = fields.Float(string="Litros", required=True)
    unit_price = fields.Float(string="Valor por litro", default=0.0)
    total = fields.Float(string="Total", compute="_compute_total", store=True)
    note = fields.Char(string="Observacao")

    # Diferencial opcional: trilha de integracao com recebimento de compras
    integration_source = fields.Selection(
        [("manual", "Manual"), ("purchase_receipt", "Recebimento de Compra")],
        string="Origem",
        required=True,
        default="manual",
    )
    source_document = fields.Char(string="Documento de Origem")
    source_partner = fields.Char(string="Fornecedor")

    @api.model
    def _default_tank_id(self):
        tank = self.env["fuel.tank"].search([], limit=1)
        return tank.id if tank else False

    @api.depends("liters", "unit_price")
    def _compute_total(self):
        for rec in self:
            rec.total = (rec.liters or 0.0) * (rec.unit_price or 0.0)

    @api.constrains("liters", "unit_price")
    def _check_values(self):
        for rec in self:
            if rec.liters <= 0:
                raise ValidationError("Litros deve ser maior que zero.")
            if rec.unit_price < 0:
                raise ValidationError("Valor por litro nao pode ser negativo.")

    @api.constrains("integration_source", "source_document")
    def _check_integration_fields(self):
        for rec in self:
            if rec.integration_source == "purchase_receipt" and not rec.source_document:
                raise ValidationError(
                    "Informe o Documento de Origem para entradas vindas de recebimento de compra."
                )

    @api.model
    def create_from_purchase_receipt(
        self,
        tank_id,
        liters,
        unit_price=0.0,
        document_ref=False,
        supplier=False,
        note=False,
    ):
        """Ponto de integracao para receber entradas a partir de recebimentos de compra."""
        return self.create(
            {
                "tank_id": tank_id,
                "move_type": "in",
                "liters": liters,
                "unit_price": unit_price,
                "integration_source": "purchase_receipt",
                "source_document": document_ref or "",
                "source_partner": supplier or "",
                "note": note or "Entrada criada por integracao de recebimento.",
            }
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for rec in records:
            if rec.move_type == "in":
                new_level = rec.tank_id.current_liters + rec.liters
                if new_level > rec.tank_id.capacity_liters:
                    raise ValidationError("Estoque excede a capacidade do tanque.")
                rec.tank_id.current_liters = new_level
            elif rec.move_type == "adjust":
                if rec.liters > rec.tank_id.capacity_liters:
                    raise ValidationError("Ajuste maior que a capacidade do tanque.")
                rec.tank_id.current_liters = rec.liters

        return records

    def write(self, vals):
        blocked = {"tank_id", "move_type", "liters", "integration_source", "source_document"}
        if blocked.intersection(vals.keys()):
            raise ValidationError(
                "Nao e permitido alterar tanque/tipo/litros/origem em movimentos ja criados. "
                "Crie um novo movimento de ajuste."
            )
        return super().write(vals)

    def unlink(self):
        raise ValidationError(
            "Nao e permitido excluir movimentacoes de estoque para preservar o historico."
        )
