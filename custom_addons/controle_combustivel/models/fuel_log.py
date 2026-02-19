from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FuelLog(models.Model):
    _name = "fuel.log"
    _description = "Abastecimento"
    _order = "date_time desc, id desc"

    tank_id = fields.Many2one(
        "fuel.tank",
        string="Tanque",
        default=lambda self: self._default_tank_id(),
    )
    vehicle_id = fields.Many2one("fleet.vehicle", string="Equipamento/Placa", required=True)
    date_time = fields.Datetime(string="Data/Hora", required=True, default=fields.Datetime.now)

    odometer = fields.Float(string="Horimetro/Odometro", required=True)
    liters = fields.Float(string="Litros", required=True)
    price_per_liter = fields.Float(string="Valor por Litro", required=True)
    total = fields.Float(string="Total", compute="_compute_total", store=True)

    responsible_user_id = fields.Many2one(
        "res.users",
        string="Usuario responsavel",
        default=lambda self: self.env.user,
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

    @api.constrains("liters", "price_per_liter", "odometer")
    def _check_values(self):
        for rec in self:
            if rec.liters <= 0:
                raise ValidationError("Litros deve ser maior que zero.")
            if rec.price_per_liter < 0:
                raise ValidationError("Valor por litro nao pode ser negativo.")
            if rec.odometer < 0:
                raise ValidationError("Horimetro/Odometro nao pode ser negativo.")

    @api.constrains("vehicle_id", "odometer")
    def _check_odometer_progress(self):
        for rec in self:
            if not rec.vehicle_id:
                continue
            domain = [
                ("vehicle_id", "=", rec.vehicle_id.id),
                ("id", "!=", rec.id),
            ]
            last = self.search(domain, order="odometer desc", limit=1)
            if last and rec.odometer < last.odometer:
                raise ValidationError(
                    "O horimetro/odometro deve ser maior ou igual ao ultimo registro do veiculo."
                )

    def _consume_from_tank(self, tank, liters):
        if liters <= 0:
            return
        if tank.current_liters < liters:
            raise ValidationError("Estoque insuficiente no tanque para este abastecimento.")
        tank.current_liters -= liters

    def _return_to_tank(self, tank, liters):
        if liters <= 0:
            return
        new_level = tank.current_liters + liters
        if new_level > tank.capacity_liters:
            raise ValidationError("A devolucao ultrapassa a capacidade do tanque.")
        tank.current_liters = new_level

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for rec in records:
            if not rec.tank_id:
                tank = self.env["fuel.tank"].search([], limit=1)
                if not tank:
                    raise ValidationError(
                        "Nenhum tanque encontrado. Crie o Tanque Principal antes de lancar abastecimentos."
                    )
                rec.tank_id = tank.id
            rec._consume_from_tank(rec.tank_id, rec.liters)

        return records

    def write(self, vals):
        stock_fields = {"tank_id", "liters"}
        before = {
            rec.id: {
                "tank": rec.tank_id,
                "liters": rec.liters,
            }
            for rec in self
        }

        result = super().write(vals)

        if stock_fields.intersection(vals.keys()):
            for rec in self:
                old_tank = before[rec.id]["tank"]
                old_liters = before[rec.id]["liters"]

                rec._return_to_tank(old_tank, old_liters)
                rec._consume_from_tank(rec.tank_id, rec.liters)

        return result

    def unlink(self):
        for rec in self:
            rec._return_to_tank(rec.tank_id, rec.liters)
        return super().unlink()


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    fuel_log_ids = fields.One2many("fuel.log", "vehicle_id", string="Abastecimentos")