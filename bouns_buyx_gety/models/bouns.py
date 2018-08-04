'''
Created on Mar 16, 2018

@author: mtloob, f_nedal
'''

from odoo import models, fields, api, _


class bouns_conf(models.Model):
    _name = 'bouns.conf'
    _description = 'bouns configuration'
    _order = 'qty_buy'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Name', copy=False)
    product_id = fields.Many2one('product.product', 'Product')
    qty_buy = fields.Integer('Buy Quantity')
    qty_fress = fields.Integer('Quantity Free')
    bonus_type = fields.Selection(selection=[('product', 'Product'), ('category', 'Category')])
    bonus_from = fields.Date('From', required=True)
    bonus_to = fields.Date('To', required=True)
    category_ids = fields.Many2many('bonus.category')

    @api.multi
    @api.onchange('bonus_type')
    def clear_data(self):
        if self.bonus_type == 'category':
            self.product_id = False
            self.qty_buy = False
            self.qty_fress = False

        if self.bonus_type == 'product':
            for rec in self.category_ids:
                rec.unlink()

    @api.model
    def create(self, vals):
        vals['name'] = 'Buy ' + str(vals['qty_buy']) + ' Get ' + str(vals['qty_fress']) + str(' for free ')
        return super(bouns_conf, self).create(vals)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.model
    # def create(self, vals):
    #     sale_id = super(SaleOrder, self).create(vals)
    #     self.apply_bouns(sale_id)
    #     return sale_id

    def apply_bouns_button(self):
        pro_dic = {}
        pro_dic1 = {}
        sale_line_objs = self.env['sale.order.line'].search([('order_id', '=', self.id), ('created_from', '=', '2')])
        if sale_line_objs:
            sale_line_objs.unlink()
        id_list = []
        for sale_line in self.order_line:
            if sale_line.original_sale_order:
                sale_line.original_sale_order.unlink()
            if sale_line.product_id:
                if pro_dic.get(sale_line.product_id.id):
                    pro_dic[sale_line.product_id.id] += sale_line.product_uom_qty
                else:
                    pro_dic[sale_line.product_id.id] = sale_line.product_uom_qty

        for sale_line in self.order_line:
            id_list = []
            if sale_line.original_sale_order:
                sale_line.original_sale_order.unlink()
            if sale_line.product_id:
                if pro_dic1.get(sale_line.product_id.id):
                    pro_dic1[sale_line.product_id.id].append(sale_line)
                    # pro_dic[sale_line.product_id.id] = id_list
                else:
                    id_list.append(sale_line)
                    pro_dic1[sale_line.product_id.id] = id_list
        product_salary = 0.0
        product_idd = 0
        has_bouns = self.env['bouns.conf'].search(
            [('bonus_type', '=', 'category'), ('bonus_from', '<', self.date_order), ('bonus_to', '>', self.date_order)],
            order='qty_buy desc')
        # remaing_qty = qty
        newLineFreeQTY = 0.0
        if has_bouns:
            for product_id, line in pro_dic1.items():
                for bouns in has_bouns:
                    if product_id in bouns.category_ids.products_ids.ids:
                        product_obj = self.env['product.product'].browse(product_id)

                        if product_salary > product_obj.lst_price or product_salary == 0:
                            product_salary = product_obj.lst_price
                            product_idd = product_id
                if pro_dic1.keys()[-1] == product_id:
                    prod_qty_temp = 0
                    for rec in pro_dic1.get(product_idd)[0]:
                        if rec.product_uom_qty < prod_qty_temp or prod_qty_temp == 0:
                            prod_qty_temp = rec.product_uom_qty
                            record_temp = rec
                    if prod_qty_temp - 1 == 0:
                        record_temp.unlink()
                    else:
                        record_temp.write({'product_uom_qty': prod_qty_temp - 1})
                    x = self.env['sale.order.line'].create({'product_id': product_idd, 'name': 'Free Quantity',
                                                            'product_uom_qty': 1.0, 'price_unit': 0.0,
                                                            'order_id': self.id, 'created_from': '2',
                                                            })

        else:
            for product_id, qty in pro_dic.items():
                has_bouns = self.env['bouns.conf'].search(
                    [('product_id', '=', product_id), ('bonus_from', '<', self.date_order),
                     ('bonus_to', '>', self.date_order)], order='qty_buy desc')
                remaing_qty = qty
                newLineFreeQTY = 0.0

                if has_bouns:
                    for bouns in has_bouns:
                        if float(remaing_qty) >= float(bouns.qty_buy):
                            free_qty = int(remaing_qty / bouns.qty_buy)
                            if free_qty < 1:
                                continue
                            newLineFreeQTY += free_qty * bouns.qty_fress
                            remaing_qty = remaing_qty - bouns.qty_buy * free_qty
                    if newLineFreeQTY:
                        self.env['sale.order.line'].create({'product_id': product_id, 'name': 'Free Quantity',
                                                            'product_uom_qty': newLineFreeQTY, 'price_unit': 0.0,
                                                            'order_id': self.id, 'created_from': '2',
                                                            'original_sale_order': sale_line.id})
        return True

    def apply_bouns(self, sale_id):
        pro_dic = {}
        pro_dic1 = {}
        sale_line_objs = self.env['sale.order.line'].search([('order_id', '=', sale_id.id), ('created_from', '=', '2')])
        if sale_line_objs:
            sale_line_objs.unlink()
        id_list = []
        for sale_line in sale_id.order_line:
            if sale_line.original_sale_order:
                sale_line.original_sale_order.unlink()
            if sale_line.product_id:
                if pro_dic.get(sale_line.product_id.id):
                    pro_dic[sale_line.product_id.id] += sale_line.product_uom_qty
                else:
                    pro_dic[sale_line.product_id.id] = sale_line.product_uom_qty

        for sale_line in sale_id.order_line:
            id_list = []
            if sale_line.original_sale_order:
                sale_line.original_sale_order.unlink()
            if sale_line.product_id:
                if pro_dic1.get(sale_line.product_id.id):
                    pro_dic1[sale_line.product_id.id].append(sale_line)
                    # pro_dic[sale_line.product_id.id] = id_list
                else:
                    id_list.append(sale_line)
                    pro_dic1[sale_line.product_id.id] = id_list
        product_salary = 0.0
        product_idd = 0
        has_bouns = self.env['bouns.conf'].search(
            [('bonus_type', '=', 'category'), ('bonus_from', '<', sale_id.date_order), ('bonus_to', '>', sale_id.date_order)],
            order='qty_buy desc')
        # remaing_qty = qty
        newLineFreeQTY = 0.0
        if has_bouns:
            for product_id, line in pro_dic1.items():
                for bouns in has_bouns:
                    if product_id in bouns.category_ids.products_ids.ids:
                        product_obj = self.env['product.product'].browse(product_id)

                        if product_salary > product_obj.lst_price or product_salary == 0:
                            product_salary = product_obj.lst_price
                            product_idd = product_id
                if pro_dic1.keys()[-1] == product_id:
                    prod_qty_temp = 0
                    for rec in pro_dic1.get(product_idd)[0]:
                        if rec.product_uom_qty < prod_qty_temp or prod_qty_temp == 0:
                            prod_qty_temp = rec.product_uom_qty
                            record_temp = rec
                    if prod_qty_temp - 1 == 0:
                        record_temp.unlink()
                    else:
                        record_temp.write({'product_uom_qty': prod_qty_temp - 1})
                    x = self.env['sale.order.line'].create({'product_id': product_idd, 'name': 'Free Quantity',
                                                            'product_uom_qty': 1.0, 'price_unit': 0.0,
                                                            'order_id': sale_id.id, 'created_from': '2',
                                                            })

        else:
            for product_id, qty in pro_dic.items():
                has_bouns = self.env['bouns.conf'].search(
                    [('product_id', '=', product_id), ('bonus_from', '<', sale_id.date_order),
                     ('bonus_to', '>', sale_id.date_order)], order='qty_buy desc')
                remaing_qty = qty
                newLineFreeQTY = 0.0

                if has_bouns:
                    for bouns in has_bouns:
                        if float(remaing_qty) >= float(bouns.qty_buy):
                            free_qty = int(remaing_qty / bouns.qty_buy)
                            if free_qty < 1:
                                continue
                            newLineFreeQTY += free_qty * bouns.qty_fress
                            remaing_qty = remaing_qty - bouns.qty_buy * free_qty
                    if newLineFreeQTY:
                        self.env['sale.order.line'].create({'product_id': product_id, 'name': 'Free Quantity',
                                                            'product_uom_qty': newLineFreeQTY, 'price_unit': 0.0,
                                                            'order_id': sale_id.id, 'created_from': '2',
                                                            'original_sale_order': sale_line.id})
        return True




    @api.multi
    def write(self, vals):
            pro_dic = {}
            sale_id = super(SaleOrder, self).write(vals)
            pro_dic = {}
            pro_dic1 = {}
            sale_line_objs = self.env['sale.order.line'].search(
                [('order_id', '=', self.id), ('created_from', '=', '2')])
            if sale_line_objs:
                sale_line_objs.unlink()
            id_list = []
            for sale_line in self.order_line:
                if sale_line.original_sale_order:
                    sale_line.original_sale_order.unlink()
                if sale_line.product_id:
                    if pro_dic.get(sale_line.product_id.id):
                        pro_dic[sale_line.product_id.id] += sale_line.product_uom_qty
                    else:
                        pro_dic[sale_line.product_id.id] = sale_line.product_uom_qty

            for sale_line in self.order_line:
                id_list = []
                # if sale_line.original_sale_order:
                #     sale_line.original_sale_order.unlink()
                if sale_line.product_id:
                    if pro_dic1.get(sale_line.product_id.id):
                        pro_dic1[sale_line.product_id.id].append(sale_line)
                        # pro_dic[sale_line.product_id.id] = id_list
                    else:
                        id_list.append(sale_line)
                        pro_dic1[sale_line.product_id.id] = id_list
            product_salary = 0.0
            product_idd = 0
            has_bouns = self.env['bouns.conf'].search(
                [('bonus_type', '=', 'category'), ('bonus_from', '<', self.date_order),
                 ('bonus_to', '>', self.date_order)],
                order='qty_buy desc')
            # remaing_qty = qty
            newLineFreeQTY = 0.0
            if has_bouns:
                print 'fasdfd'
                for product_id, line in pro_dic1.items():
                    for bouns in has_bouns:
                        if product_id in bouns.category_ids.products_ids.ids:
                            product_obj = self.env['product.product'].browse(product_id)

                            if product_salary > product_obj.lst_price or product_salary == 0:
                                product_salary = product_obj.lst_price
                                product_idd = product_id
                    if pro_dic1.keys()[-1] == product_id:
                        print  '454545'
                        prod_qty_temp = 0
                        for rec in pro_dic1.get(product_idd)[0]:
                            if rec.product_uom_qty < prod_qty_temp or prod_qty_temp == 0:
                                prod_qty_temp = rec.product_uom_qty
                                record_temp = rec
                        print prod_qty_temp
                        if prod_qty_temp - 1 == 0:
                            print record_temp.product_id.name
                            print record_temp.name
                            record_temp.unlink()
                        else:
                            print 'jfksadhfjkls'
                            record_temp.write({'product_uom_qty': prod_qty_temp - 1})
                        x = self.env['sale.order.line'].create({'product_id': product_idd, 'name': 'Free Quantity',
                                                                'product_uom_qty': 1.0, 'price_unit': 0.0,
                                                                'order_id': self.id, 'created_from': '2',
                                                                })

            else:
                print  '8888888888'
                for product_id, qty in pro_dic.items():
                    has_bouns = self.env['bouns.conf'].search(
                        [('product_id', '=', product_id), ('bonus_from', '<', self.date_order),
                         ('bonus_to', '>', self.date_order)], order='qty_buy desc')
                    remaing_qty = qty
                    newLineFreeQTY = 0.0
                    print '99999'
                    if has_bouns:
                        for bouns in has_bouns:
                            if float(remaing_qty) >= float(bouns.qty_buy):
                                free_qty = int(remaing_qty / bouns.qty_buy)
                                if free_qty < 1:
                                    continue
                                newLineFreeQTY += free_qty * bouns.qty_fress
                                remaing_qty = remaing_qty - bouns.qty_buy * free_qty
                        if newLineFreeQTY:
                            print '896656'
                            self.env['sale.order.line'].create({'product_id': product_id, 'name': 'Free Quantity',
                                                                'product_uom_qty': newLineFreeQTY, 'price_unit': 0.0,
                                                                'order_id': self.id, 'created_from': '2',
                                                                'original_sale_order': sale_line.id})
            return True
            # print 'fasfsdf',vals
            # if self.order_line:
            #     print 'ooooooooooooo'
            #     sale_line_objs = self.env['sale.order.line'].search(
            #         [('order_id', '=', self.id), ('created_from', '=', '2')])
            #     if sale_line_objs:
            #         sale_line_objs.unlink()
            #     for sale_line in self.order_line:
            #         if sale_line.product_id:
            #             if pro_dic.get(sale_line.product_id.id):
            #                 pro_dic[sale_line.product_id.id] += sale_line.product_uom_qty
            #             else:
            #                 pro_dic[sale_line.product_id.id] = sale_line.product_uom_qty
            #     for product_id, qty in pro_dic.items():
            #         has_bouns = self.env['bouns.conf'].search([('product_id', '=', product_id)], order='qty_buy desc')
            #         remaing_qty = qty
            #         newLineFreeQTY = 0.0
            #         if has_bouns:
            #             for bouns in has_bouns:
            #                 if float(remaing_qty) >= float(bouns.qty_buy):
            #                     free_qty = int(remaing_qty / bouns.qty_buy)
            #                     if free_qty < 1:
            #                         continue
            #                     newLineFreeQTY += free_qty * bouns.qty_fress
            #                     remaing_qty = remaing_qty - bouns.qty_buy * free_qty
            #             if newLineFreeQTY:
            #                 self.env['sale.order.line'].create({'product_id': product_id, 'name': 'Free Quantity',
            #                                                     'product_uom_qty': newLineFreeQTY, 'price_unit': 0.0,
            #                                                     'order_id': self.id, 'created_from': '2',
            #                                                     'original_sale_order': sale_line.id})
            # return sale_id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    has_bouns = fields.Boolean('Has Bouns')
    product_bouns_id = fields.Many2one('bouns.conf', 'Bouns')
    created_from = fields.Selection([('1', 'createduser'), ('2', 'createdsystem')], 'created from', default='1')
    original_sale_order = fields.Many2one('sale.order.line', 'original sale order')

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            has_bouns = self.env['bouns.conf'].search([('product_id', '=', self.product_id.id)])
            if has_bouns:
                res['has_bouns'] = True
                self.has_bouns = True
        return res

    @api.multi
    def action_show_bouns(self):
        context = dict(self._context or {})
        product_id = context['product_id']
        has_bouns = self.env['bouns.conf'].search([('product_id', '=', product_id)])
        if has_bouns:
            return {
                'name': _('Products Bouns'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'bouns.conf',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', has_bouns.ids)],
                'target': 'new',
                'context': context,
            }
        return True


class BonusCategory(models.Model):
    _name = 'bonus.category'

    name = fields.Char('Name', required=True)
    products_ids = fields.Many2many(comodel_name='product.product', string='Product')
