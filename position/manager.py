import time
import math
class Manager:
	def __init__(self, **kwargs):
		self._position_class = kwargs['position_class']
		self._position_list = dict()


	#pass detail as constructor of position detail is a diction like obj
	def add(self, **kwargs):
		#use timestamp as id
		position_id = math.floor( float( time.time() ) )
		new_position = self._position_class(detail=kwargs['detail'], id=position_id)
		self._position_list[new_position.id] = new_position
		return new_position

	def delete(self, **kwargs):
		position_id = kwargs['id']
		position = self._position_list[position_id]
		del self._position_list[position_id]
		return True

	def show_position_list(self):
		pass

