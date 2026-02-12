from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FuelStockMove(models.Model):
    _name = "fuel.stock.move"
    _description = "Movimentação do Tanque (Entrada)"
    _order = "date desc, id desc"

    tank_id = fields.Many2one("fuel.tank", string="Tanque", required=True)
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

    note = fields.Char(string="Observação")

    @api.depends("liters", "unit_price")
    def _compute_total(self):
        for rec in self:
            rec.total = (rec.liters or 0.0) * (rec.unit_price or 0.0)

    @api.constrains("liters")
    def _check_liters(self):
        for rec in self:
            if rec.liters <= 0:
                raise ValidationError("Litros deve ser maior que zero.")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.move_type == "in":
                rec.tank_id.current_liters += rec.liters
            elif rec.move_type == "adjust":
                # Ajuste define o estoque para o valor informado em litros
                rec.tank_id.current_liters = rec.liters

            if rec.tank_id.current_liters > rec.tank_id.capacity_liters:
                raise ValidationError("Estoque excede a capacidade do tanque.")
        return records
