from django.contrib import admin
from ohm2_handlers_light import models
from ohm2_handlers_light import utils as h_utils

class BaseAdmin(admin.ModelAdmin):
	exclude = (
		"identity",
		"created",
		"last_update",
	)

	def save_model(self, request, obj, form, change):
		obj = form.instance
		if not change or len(obj.identity) == 0:
			obj.identity = h_utils.db_unique_random(type(obj))
		super(type(self), self).save_model(request, obj, form, change)
