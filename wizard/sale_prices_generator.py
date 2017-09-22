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
    price1_mm = fields.Float('Price/mm 1')
    price2_mm = fields.Float('Price/mm 2')
    price3_mm = fields.Float('Price/mm 3')
    raw_material_thousand = fields.Float(
        'Raw material per thousand', compute='_compute_raw_material_thousand')
    labour_thousand = fields.Float(
        'Labour force per thousand', compute='_compute_labour_thousand')
    box_cost_thousand = fields.Float(
        'Cost of boxes per thousand', compute='_compute_box_cost_thousand')
    total_cost_thousand = fields.Float(
        'Total cost per thousand', compute='_compute_total_cost_thousand')
    sale_price_range = fields.One2many(
        comodel_name='pky.pvc.price.range.thousand',
        inverse_name='sale_price_generator_wizard_id',
        string='Range of prices per thousands'
    )
    min_volume_75 = fields.Float(
        'Minimum possible due to high volume 75%',
        compute='_compute_min_volume_75')
    cost_roll = fields.Float('Cost per roll', compute='_compute_cost_roll')
    sale_price_roll_40 = fields.Float(
        'Sale price per roll 40%',
        compute='_compute_sale_price_roll')
    sale_price_roll_50 = fields.Float(
        'Sale price per roll 50%',
        compute='_compute_sale_price_roll')
    sale_price_roll_60 = fields.Float(
        'Sale price per roll 60%',
        compute='_compute_sale_price_roll')
    sale_price_roll_70 = fields.Float(
        'Sale price per roll 70%',
        compute='_compute_sale_price_roll')

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
            if rec.thousands_qty and rec.type and rec.cardboard_box_cost:
                if rec.type == 'preformed':
                    thousand_box_by_flat_width = PkyPvcPreformed.search(
                        [('flat_width_mm', '=', rec.flat_width_mm)])
                    if thousand_box_by_flat_width:
                        rec.box_cost = round(rec.thousands_qty / \
                            thousand_box_by_flat_width[0].thousands_box, 0) \
                            * rec.cardboard_box_cost

    @api.depends(
        'price1_mm',
        'price2_mm',
        'price3_mm',
        'cut_mm',
        'inks',
        'flat_width_mm')
    def _compute_raw_material_thousand(self):
        """Computes value of field raw_material_thousand"""

        for rec in self:
            if rec.flat_width_mm and rec.cut_mm:
                price = 0
                if rec.inks == 0:
                    price = rec.price1_mm
                elif rec.inks == 1 or rec.inks == 2:
                    price = rec.price2_mm
                elif rec.inks == 3 or rec.inks == 4:
                    price = rec.price3_mm

                if price > 0:
                    rec.raw_material_thousand = rec.flat_width_mm * price / \
                        (500 / rec.cut_mm)

    @api.depends(
        'employee_cutting_salary',
        'cutting_time_days',
        'preformed_time_days',
        'thousands_qty',
        'employee_pair_preformed_salary')
    def _compute_labour_thousand(self):
        """Computes value of field labour_thousand"""

        for rec in self:
            rec.labour_thousand = (rec.employee_cutting_salary *
                rec.cutting_time_days / rec.thousands_qty) + (
                rec.employee_pair_preformed_salary * rec.preformed_time_days /
                rec.thousands_qty)

    @api.depends('thousands_qty', 'box_cost')
    def _compute_box_cost_thousand(self):
        """Computes value of field box_cost_thousand"""

        for rec in self:
            rec.box_cost_thousand = rec.box_cost / rec.thousands_qty

    @api.depends(
        'box_cost_thousand',
        'labour_thousand',
        'raw_material_thousand')
    def _compute_total_cost_thousand(self):
        """Computes value of field total_cost_thousand"""

        for rec in self:
            rec.total_cost_thousand = rec.box_cost_thousand + \
                rec.labour_thousand + rec.raw_material_thousand

    @api.depends('total_cost_thousand')
    def _compute_min_volume_75(self):
        """Computes value of field min_volume_75"""

        for rec in self:
            rec.min_volume_75 = round((rec.total_cost_thousand * 100) / 75, 2)

    @api.depends(
        'price1_mm',
        'price2_mm',
        'price3_mm',
        'inks',
        'flat_width_mm')
    def _compute_cost_roll(self):
        """Computes value of field cost_roll"""

        for rec in self:
            if rec.inks == 0:
                rec.cost_roll = rec.flat_width_mm * rec.price1_mm
            elif rec.inks == 1 or rec.inks == 2:
                rec.cost_roll = rec.flat_width_mm * rec.price2_mm
            elif rec.inks == 3 or rec.inks == 4:
                rec.cost_roll = rec.flat_width_mm * rec.price3_mm

    @api.depends('cost_roll')
    def _compute_sale_price_roll(self):
        """Computes value of fields sale_price_roll_40, sale_price_roll_50,
        sale_price_roll_60, sale_price_roll_70."""

        for rec in self:
            rec.sale_price_roll_40 = rec.cost_roll / 0.4
            rec.sale_price_roll_50 = rec.cost_roll / 0.5
            rec.sale_price_roll_60 = rec.cost_roll / 0.6
            rec.sale_price_roll_70 = rec.cost_roll / 0.7

class PkyPvcPreformed(models.Model):
    _name = 'pky.pvc.preformed'

    flat_width_mm = fields.Float('Flat Width (mm)')
    cut_mm = fields.Float('Cut (mm)')
    standard_turn = fields.Float('Standard / Turn')
    thousands_box = fields.Float('Thousand / Box')


class PkyPvcPriceRangeThousand(models.TransientModel):
    _name = 'pky.pvc.price.range.thousand'

    rolls_qty = fields.Char('Quantity of Rolls')
    lower_limit = fields.Float('From')
    upper_limit = fields.Float('To')
    percentage_cutting = fields.Float('Cutting percentage')
    price = fields.Float('Sale Price')
    sale_price_generator_wizard_id = fields.Many2one(
        'sale.prices.generator',
        'Sale price generator'
    )
