from odoo import api, fields, models
from odoo import tools, _
from odoo.modules.module import get_module_resource
import base64
import json
import io
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class Department(models.Model):
	_name = 'department.detail'
	_description = "Department"

	name = fields.Char(string="Name", default ="A")
	code = fields.Char(string="Code")
	fold = fields.Boolean('Folded?')

class Sendq(models.Model):
	_name = 'sendq.detail'
	_description = "Send Quotation"

	name = fields.Char(string="Name", default ="A")
	mailid= fields.Char(string="Code")
	cont = fields.Many2one('book.detail', string="Sample Book Details")
	#send_ids = fields.Many2one('book.detail', string="Simple Book Details")



 
class author(models.Model):

	_name = 'book.detail'
	_description = 'Simple Book'

	filename = fields.Char("File Name")
	json_binary = fields.Binary('Upload')

	@api.model
	def _default_image(self):
		image_path = get_module_resource('tests', 'static/src/img', 'apple.png')
		# return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))
		# return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))
		# return tools.image_resize_image_big(open(image_path, 'rb').base64.b64encode(f.read())

	#name = fields.Char(string="Name", required=True)
	name = fields.Char(string="Title", required=True)
	desc = fields.Text(string="Description")
	author = fields.Char(string="Author", required=False)
	nature = fields.Selection([('story','STORY'),('bibiliography','BIBILIOGRAPHY'),('communitism','COMMUNITISM'),('naval','NAVAL')], required=False)
	date = fields.Date("	Date of writing")
	day = fields.Datetime("Upadated Date")
	stage_fold = fields.Boolean("Stage Folded?", compute='_compute_stage_fold')
	reference_Doc = fields.Reference([('book.detail' , 'ref document')])
	# attachment = fields.Binary("Files")
	book_id = fields.Many2one('department.detail', string="Category")
	partner_id = fields.Many2one('res.partner', string='Customer')
	family_detail_ids = fields.One2many('family.detail', 'author_det_id', string='Book Details')
	tag_ids = fields.Many2many('author.tag.detail', string="Tags")
	send_id = fields.One2many('sendq.detail', 'cont', string='Sending')
	state = fields.Selection([('draft', "Draft"),('confirmed', "Confirmed"),('done', "Done"),('cancel', "Cancelled")], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
	# stage_id = fields.Char(string="Stage")
	# procurement_group_id = Many2one('procurement.group', 'Procurement Group', copy=False)
	# procurement_ids = fields.One2many('procurement.order','sale_line_id', string='Procurements')
	effort_estimate = fields.Integer('Effort Estimate')
	image = fields.Binary( default=_default_image, attachment=True,
        help="This field holds the image used as photo for the book, limited to 1024x1024px.")

	# image_medium = fields.Binary("Medium-sized photo", attachment=True,
        # help="Medium-sized photo of the employee. It is automatically "
             # "resized as a 128x128px image, with aspect ratio preserved. "
             # "Use this field in form views or some kanban views.")

	@api.multi
	def import_lines(self):
		created_val = []
		temp = []
		try:
			data = base64.b64decode(self.json_binary)
			file_input = io.StringIO(data.decode("utf-8"))
			file_input.seek(0)
			reader = json.reader(file_input, delimiter=',', lineterminator='\r\n')
			reader_info = []
			reader_info.extend(reader)
			keys = reader_info[0]
		except Exception as e:
			raise UserError(_("Invalid file %s" % tools.ustr(e)))
		for i in range(1, len(reader_info)):
			field = reader_info[i]
			values = dict(zip(keys, field))
			if values:
				created_val.append(values['name'])
		for val in created_val:
			print (val, "valvalval")
			for line in self.move_line_ids:
				if val not in temp:
					if not line.author:
						line.write({'author': val})
						temp.append(val)

		return True


	@api.depends('book_id.fold')
	def _compute_stage_fold(self):
		for task in self:
			task.stage_fold = task.book_id.fold





	@api.multi
	def action_draft(self):
	 	orders = self.filtered(lambda s: s.state in ['cancel', 'confirmed'])
	 	orders.write({
            'state': 'draft',
            # 'procurement_group_id': False,
         })
	 	orders.mapped('family_detail_ids').mapped('procurement_ids').write({'sale_line_id': True})
		# self.state='draft'

	@api.multi
	def action_confirm(self):

		self.state='confirmed'

	@api.multi
	def action_done(self):
		self.state='done'

	# def _prepare_procurement_group(self):
		# return {'name': self.name}


	@api.multi
	def action_cancel(self):
		self.write({'state': 'cancel'})

	@api.multi
	def action_print(self):
		self.filtered(lambda s: s.state == 'draft').write({'state': 'confirmed'})
		return self.env['report'].get_action(self, 'tests.report_book1')
	

	@api.onchange('nature')
	def onchange_nature(self):
		if self.nature in('naval','NAVAL'):
			self.desc = self.nature


	@api.multi
	def action_send_quotation(self):
	 	return {
	 		'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sendq.detail',
            'name': 'Generate Quotation',
            # 'views': [(compose_form_id, 'form')],
            # 'view_id': sendq_form_view,
            # 'target': 'new',
            # 'context': ctx,

			}
		#super(author,self).action_draft()
		# for line in self.family_detail_ids:
			# line.write({'notes':"DONE"})


	# @api.multi
	# @api.returns('self')
	# def action_send(self):

		# return sendq
		# for line in self.send_id:

			# line.name 
			# line.mailid
			#return res
			# line.write({'notes':"DONE"})
class Family(models.Model):
	_name = 'family.detail'
	_description = 'Book Detail'
  
	name = fields.Char(string="Name")
	# effort_estimate = fields.Integer('Effort Estimate')
	attachment = fields.Binary("Files")
	# date = fields.Date("	Date of writing")
	# day = fields.Datetime("Upadated Date")
	# book_id = fields.Many2one('department.detail', string="Category")
	# age = fields.Integer(string="Age")
	# status = fields.Selection([('alive','Alive'),('not alive','Not Alive')])
	#procurement_ids = fields.One2many('procurement.order','sale_line_id', string='Procurements')
	author_det_id = fields.Many2one('book.detail', string="Simple Book Details")
	notes = fields.Char(string="NOTE")
	

	# @api.multi
	# def action_drafts(self):
	# 	super(author,self).action_draft()
	# 	self.write({'note':"DONE"})


	



class Tags(models.Model):
	_name = 'author.tag.detail'
	_description = "Tags"

	name = fields.Char(string="Name")
	product = fields.Char(string="Product")

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    # _inherits = {'sale.order': 'collect'}

	# collect = fields.Many2one('sale.order', help='This is a many2one field in ')    
    due_date = fields.Date("Due Date")
    cust_ref = fields.Char("Customer Reference")
    costprice = fields.Float("Buy price")
    shippingcost = fields.Float("Shipping Cost")
    Tax = fields.Float("Taxes")

    
    @api.multi
    def action_cancel(self):
        super(SaleOrder, self).action_cancel()
        self.write({'note': "DONE"})


    @api.onchange('costprice')
    def onchange_costprice(self):
    	if self.costprice:
    	    self.shippingcost = self.costprice*2

    # @api.onchange('amount_tax')
    # def onchange_amount_tax(self):
    # 	if self.amount_tax:
    # 		self.Tax = self.amount_tax

    @api.multi
    def action_confirm(self):
    	super(SaleOrder, self).action_confirm()
    	self.Tax = self.amount_tax*2

#class on_change_function(models.Model):
    #_inherit='sale.order'

    
   # def on_change_price(self,cr,user,ids,CostPrice,ShippingCost,context=None):
	#    total = CostPrice + ShippingCost
     #   res = { 'value': { 'standar_price': total } }
      #  retun res-->

   
class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	due_date = fields.Date("Due Date")