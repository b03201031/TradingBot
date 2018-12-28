import time
import math
class Manager:
	def __init__(self, **kwargs):
		self._position_class = kwargs['position_class']
		self._position_list = list()


	#pass detail as constructor of position detail is a diction like obj
	def add(self, **kwargs):
		#use timestamp as id
		position_id = math.floor( float( time.time() ) )
		new_position = self._position_class(detail=kwargs['detail'], id=position_id)
		new_position = self._position_list.append(new_position) 
		return new_position


	def show_position_list(self):
		pass

