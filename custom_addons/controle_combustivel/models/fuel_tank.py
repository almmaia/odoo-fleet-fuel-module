from odoo import models, fields


class FuelTank(models.Model):
    _name = "fuel.tank"
    _description = "Tanque de Combustível"

    name = fields.Char(string="Nome", required=True)
    capacity_liters = fields.Float(string="Capacidade (L)", required=True, default=6000.0)
    current_liters = fields.Float(string="Estoque atual (L)", required=True, default=0.0)

    active = fields.Boolean(default=True)
