from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FuelLog(models.Model):
    _name = "fuel.log"
    _description = "Abastecimento"
    _order = "date_time desc, id desc"

    # ⚠️ NÃO pode ser required=True no banco se o default depende de XML
    tank_id = fields.Many2one(
        "fuel.tank",
        string="Tanque",
        default=lambda self: self._default_tank_id(),
    )

    vehicle_id = fields.Many2one("fleet.vehicle", string="Equipamento/Placa", required=True)
    date_time = fields.Datetime(string="Data/Hora", required=True, default=fields.Datetime.now)

    odometer = fields.Float(string="Horímetro/Odômetro", required=True)
    liters = fields.Float(string="Litros", required=True)
    price_per_liter = fields.Float(string="Valor por Litro", required=True)

    total = fields.Float(string="Total", compute="_compute_total", store=True)

    responsible_user_id = fields.Many2one(
        "res.users",
        string="Usuário responsável",
        default=lambda self: self.env.user.id,
        readonly=True,
    )
    driver = fields.Char(string="Motorista")

    km_rodado = fields.Float(string="KM Rodado", compute="_compute_metrics", store=True)
    consumo = fields.Float(string="KM/L", compute="_compute_metrics", store=True)
    custo_km = fields.Float(string="Custo por KM", compute="_compute_metrics", store=True)

    @api.model
    def _default_tank_id(self):
        tank = self.env["fuel.tank"].search([], limit=1)
        return tank.id if tank else False

    @api.depends("liters", "price_per_liter")
    def _compute_total(self):
        for rec in self:
            rec.total = (rec.liters or 0.0) * (rec.price_per_liter or 0.0)

    @api.depends("vehicle_id", "odometer", "liters", "total")
    def _compute_metrics(self):
        for rec in self:
            rec.km_rodado = 0.0
            rec.consumo = 0.0
            rec.custo_km = 0.0

            if not rec.vehicle_id or not rec.odometer:
                continue

            domain = [
                ("vehicle_id", "=", rec.vehicle_id.id),
                ("odometer", "<", rec.odometer),
            ]
            # evita NewId
            if isinstance(rec.id, int) and rec.id:
                domain.append(("id", "!=", rec.id))

            last = self.search(domain, order="odometer desc", limit=1)
            if not last:
                continue

            km = rec.odometer - (last.odometer or 0.0)
            if km <= 0:
                continue

            rec.km_rodado = km
            if rec.liters:
                rec.consumo = km / rec.liters
            rec.custo_km = rec.total / km

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for rec in records:
            # Garante tanque (agora que o banco já tem dados)
            if not rec.tank_id:
                tank = self.env["fuel.tank"].search([], limit=1)
                if not tank:
                    raise ValidationError("Nenhum tanque encontrado. Crie o Tanque Principal antes de lançar abastecimentos.")
                rec.tank_id = tank.id

            # Abastecimento reduz estoque
            if rec.tank_id.current_liters < rec.liters:
                raise ValidationError("Estoque insuficiente no tanque para este abastecimento.")
            rec.tank_id.current_liters -= rec.liters

        return records


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    fuel_log_ids = fields.One2many("fuel.log", "vehicle_id", string="Abastecimentos")
