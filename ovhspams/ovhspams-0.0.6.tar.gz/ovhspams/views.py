import colander
import deform.widget
import ovh
import json
import sys
from ovhspams import domaines

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

import pdb

# Configuration ===============================================================
version="0.0.2"

# Boite mail destination
dst_mbx = 'postmaster'
spm_mbx = 'spam'

# =============================================================================
# =============================================================================
class SpamViews(object):

	def __init__(self, request):
		self.request = request

		# Init des domaines à partir du fichier .ini
		doms = eval(self.request.registry.settings['domaines'])
		self.doms = domaines.Domaine(doms)
		#pdb.set_trace()

	def addspam(self, domn, cnt, form):
		"""Ajout d'un spam
			Le spam cnt est ajouté au domaine domn.
			Les emails contenant 'cnt' sont bloqués
		"""
		
		self.doms.set_dom(domn)
		client = ovh.Client(
			endpoint = self.doms.get_ep(),
			application_key = self.doms.get_ak(),
			application_secret = self.doms.get_sc(),
			consumer_key = self.doms.get_ck(),
		)
		try:
			result = client.post('/email/domain/' + self.doms.get_dm() + '/account/' + dst_mbx + '/filter', 
				action = 'redirect', # Required: Action of filter (type: domain.DomainFilterActionEnum)
				actionParam = spm_mbx + '@' + self.doms.get_dm(), # Action parameter of filter (type: string)
				active = True, # Required: If true filter is active (type: boolean)
				header = 'From', # Required: Header to be filtered (type: string)
				name = cnt, # Required: Filter name (type: string)
				operand = 'contains', # Required: Rule of filter (type: domain.DomainFilterOperandEnum)
				priority = 2, # Required: Priority of filter (type: long)
				value = cnt, # Required: Rule parameter of filter (type: string)
			)
		#except:
		except Exception as e:
			# provoquer une exception sur le formulaire pour le champ "contenu"
			exc = colander.Invalid(form, "Impossible d'ajouter le SPAM : ")
			#exc['contain'] = str(sys.exc_info()[0])
			exc['contain'] = str(e)
			form.error = exc
			form.widget.handle_error(form, exc)
			raise deform.exception.ValidationFailure(form, None, form.error)

	@property
	def spam_entry_form(self):
		class SpamEntry(colander.MappingSchema):
			domaine = colander.SchemaNode(colander.String(),
				widget = deform.widget.RadioChoiceWidget(values=[(x, x) for x in self.doms.get_dom_lst()]),
				validator=colander.OneOf(self.doms.get_dom_lst()))
			contain = colander.SchemaNode(colander.String())

		schema = SpamEntry()
		submbtn = deform.Button('submit', title="Ajout comme SPAM")
		return deform.Form(schema, buttons=(submbtn,))

	@property
	def reqts(self):
		return self.spam_entry_form.get_widget_resources()

	@property
	def result(self):
		if hasattr(self, 'resultat'):
			return self.resultat
		return ''

	@view_config(route_name='home', renderer='templates/mytemplate.pt')
	def spam_view(self):

		form = self.spam_entry_form
		
		if 'submit' in self.request.params:
			controls = self.request.POST.items()
			try:
				appstruct = form.validate(controls)
				self.addspam(appstruct['domaine'], appstruct['contain'], form)
			except deform.ValidationFailure as e:
				#pdb.set_trace()
				# Form is NOT valid
				return dict(form=e.render())

			else:
				# Un petit message
				self.resultat = 'Spam "' + appstruct['contain'] + '" ajouté à ' + appstruct['domaine']
				# Effacer le contenu et réafficher le formulaire
				appstruct['contain'] = ''

			return dict(form=form.render(appstruct))

		return dict(form=form.render())

