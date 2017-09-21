# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017 Humanytek (<www.humanytek.com>).
#    Manuel Márquez <manuel@humanytek.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import api, fields, models
from openerp.tools.translate import _


class SalePricesGenerator(models.TransientModel):
    """
    This wizard will generate prices based on parameters asociated to the
    operations of pvc.
    """

    _name = "sale.prices.generator"
    _description = """This wizard will generate quotations based on parameters
    asociated to the operations of pvc."""

    flat_width_mm = fields.Float('Flat Width (mm)')
    cut_mm = fields.Float('Cut (mm)')
    inks = fields.Float('Inks')
    thousands_qty = fields.Float('Quantity of thousands')
    type = fields.Selection(
        [('guarantee_seal', 'Guanrantee Seal'), ('preformed', 'Preformed'),],
        'Type')
    amount = fields.Float('Amount')
    thousands_per_roll = fields.Float(compute='_compute_thousands_per_roll')
    total_seven_rolls = fields.Float(compute='_compute_total_seven_rolls')
    qty_rolls_to_order = fields.Float(compute='_compute_qty_rolls_to_order')
    cutting_time_days = fields.Float(compute='_compute_cutting_time_days')
    preformed_time_days = fields.Float(compute='_compute_preformed_time_days')
    employee_cutting_salary = fields.Float('Salary of Cutting Employee')
    employee_pair_preformed_salary = fields.Float('Salary / Pair Preformed')
    cardboard_box_cost = fields.Float('Cardboard Box Cost')
    box_cost = fields.Float('Cost of Boxes', compute='_compute_box_cost')

    @api.depends('cut_mm')
    def _compute_thousands_per_roll(self):
        """Computes value of field thousands_per_roll"""

        for rec in self:
            if rec.cut_mm:
                rec.thousands_per_roll = 500 / rec.cut_mm

    @api.depends('thousands_per_roll')
    def _compute_total_seven_rolls(self):
        """Computes value of field total_seven_rolls"""

        for rec in self:
            if rec.thousands_per_roll:
                rec.total_seven_rolls = thousands_per_roll * 7

    @api.depends('thousands_qty', 'thousands_per_roll')
    def _compute_qty_rolls_to_order(self):
        """Computes value of field qty_rolls_to_order"""

        for rec in self:
            if rec.thousands_qty and rec.thousands_per_roll:
                rec.qty_rolls_to_order = \
                    rec.thousands_qty / rec.thousands_per_roll

    @api.depends('thousands_qty', 'cut_mm')
    def _compute_cutting_time_days(self):
        """Computes value of field cutting_time_days"""

        for rec in self:
            if rec.thousands_qty and rec.cut_mm:
                rec.cutting_time_days = rec.thousands_qty / \
                    ((-0,3538 * rec.cut_mm) + 110,77)

    @api.depends('thousands_qty', 'type', 'flat_width_mm')
    def _compute_preformed_time_days(self):
        """Computes value of field preformed_time_days"""

        PkyPvcPreformed = self.env['pky.pvc.preformed']
        for rec in self:
            if rec.thousands_qty and rec.type and rec.flat_width_mm:
                if rec.type == 'preformed':
                    preformed_by_flat_width = PkyPvcPreformed.search(
                        [('flat_width_mm', '=', rec.flat_width_mm)])
                    if preformed_by_flat_width:
                        rec.preformed_time_days = rec.thousands_qty / \
                            preformed_by_flat_width[0].standard_turn

    @api.depends('thousands_qty', 'type', 'cardboard_box_cost', 'flat_width_mm')
    def _compute_box_cost(self):
        """Computes value of field box_cost"""

        PkyPvcPreformed = self.env['pky.pvc.preformed']
        for rec in self:
            if rec.thousands_qty and rec.type and rec.box_cost:
                if rec.type == 'preformed':
                    thousand_box_by_flat_width = PkyPvcPreformed.search(
                        [('flat_width_mm', '=', rec.flat_width_mm)])
                    if thousand_box_by_flat_width:
                        rec.box_cost = round(rec.thousands_qty / \
                            thousand_box_by_flat_width[0].thousands_box, 0) \
                            * rec.cardboard_box_cost


class PkyPvcPreformed(models.Model):
    _name = 'pky.pvc.preformed'

    flat_width_mm = fields.Float('Flat Width (mm)')
    cut_mm = fields.Float('Cut (mm)')
    standard_turn = fields.Float('Standard / Turn')
    thousands_box = fields.Float('Thousand / Box')
