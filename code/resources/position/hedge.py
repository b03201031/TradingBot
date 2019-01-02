from .manager import Manager as manager_parent
from .position import Position as position_parent

class Manager(manager_parent):

	def show_list(self):
		for position in self._position_list:
			print('position_manager(show_list)')
			print('id: ', position.id)
			print('future:', position.future['price'])
			print('margin:', position.margin['price'])
		return True

	def write_list(self):
		pass

class Position(position_parent):
	def __init__(self, **kwargs):
		self.future = kwargs['detail']['future']
		self.margin = kwargs['detail']['margin']
		self.id = kwargs['id']

	def cost(self):
		cost = dict()
		cost['future_price'] = self.future['price']
		cost['spot_price'] = self.margin['price']
		return cost
