"""This module provides a function `url_for_obj` to get
the correct URL for a given object. Classes are registered to endpoints to
handle objects of that type using a decorator. Parameters for the view are
taken from attributes of the object or mapped in the decorator.

Let's say you have a class:

class Employee(db.Model):
	__tablename__ = 'employees'

	id = Column(Integer, primary_key=True)

And a view for an individual employee:

@blueprint.route('/employee/<int:id>')
@url_for_obj.register(Employee)
def employee(id):
	employee = Employee.query.get_or_404(id)
	return render_template('employee.html', employee=employee)

You can now call `url_for_obj(some_employee)` instead of
`url_for('.employee', id=some_employee.id)`

By default, endpoint arguments will be taken from attributes
of the passed object. You can also specify a mapping of how to
generate the parameters from the object.

@blueprint.route('/employee/<dept>/<employee_name>')
@url_for_obj.register(models.Employee, {
	'dept': lambda employee: employee.department.name,
	'employee_name': lambda employee: employee.name,
	})
def employee(dept, employee_name):
	...

Add the url_for_obj function to the template context so you can use it in
templates.
Where your blueprint is defined:

@blueprint.context_processor
def context_processor():
	return {
		'url_for_obj': url_for_obj.url_for_obj,
		}

"""

# TODO make this an extension
#	add url_for_obj to context in extension init_app
#	store class_function_mapping in app context
#	Don't assume it's part of a blueprint by adding '.' before the function name
# 	  Is there a way of checking? Should it be an option in register?

from inspect import signature

from flask import url_for

class_function_mapping = {}


def url_for_obj(obj):
	obj_type = type(obj)
	try:
		render_func, get_funcs = class_function_mapping[obj_type]
	except KeyError:
		raise ValueError('No view function registered for {}'.format(obj_type))
	kwargs = {}
	for arg in signature(render_func).parameters:
		if arg in get_funcs:
			kwargs[arg] = get_funcs[arg](obj)
		else:
			kwargs[arg] = getattr(obj, arg)
	return url_for('.' + render_func.__name__, **kwargs)


def register(class_, get_funcs={}):
	""" A decorator to register a function as the way to display an object of
	class_
	"""
	def decorator(func):
		class_function_mapping[class_] = (func, get_funcs)
		return func
	return decorator
