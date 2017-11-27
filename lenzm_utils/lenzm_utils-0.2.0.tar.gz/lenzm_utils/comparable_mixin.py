"""Mixins to implement rich comparison based on a key."""
import abc


class ComparableMixin():
	"""
	A class inheriting from ComparableMixin must implement only two functions to
	get all comparison methods.

	`_cmp_key` returns a key for comparing the objects.
	`_is_valid_operand` takes another object and determines if this class knows
		how to compare them.
	"""
	# TODO this should have a metaclass of abc.ABCMeta but I don't feel like
	# dealing with the metaclass conflict when using this with other Mixins that
	# have metaclasses (eg. SQLAlchemy models)

	@classmethod
	def _is_valid_operand(cls, other):
		raise NotImplementedError()

	@abc.abstractmethod
	def _cmp_key(self):
		raise NotImplementedError()

	def __eq__(self, other):
		if not self._is_valid_operand(other):
			return False
		return self._cmp_key() == other._cmp_key()

	def __ne__(self, other):
		if not self._is_valid_operand(other):
			return True
		return self._cmp_key() != other._cmp_key()

	def __gt__(self, other):
		if not self._is_valid_operand(other):
			return NotImplemented
		return self._cmp_key() > other._cmp_key()

	def __ge__(self, other):
		if not self._is_valid_operand(other):
			return NotImplemented
		return self._cmp_key() >= other._cmp_key()

	def __lt__(self, other):
		if not self._is_valid_operand(other):
			return NotImplemented
		return self._cmp_key() < other._cmp_key()

	def __le__(self, other):
		if not self._is_valid_operand(other):
			return NotImplemented
		return self._cmp_key() <= other._cmp_key()

	def __hash__(self):
		return hash(self._cmp_key())


class ComparableIsInstanceMixin(ComparableMixin):
	"""This class can compare to instances of the class."""

	@classmethod
	def _is_valid_operand(cls, other):
		return isinstance(other, cls)


class ComparableSameClassMixin(ComparableMixin):
	"""This class can compare to the same exact class."""

	@classmethod
	def _is_valid_operand(cls, other):
		return other.__class__ == cls
