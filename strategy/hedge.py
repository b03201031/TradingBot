from .strategy import strategy

class Hedge(strategy):
	
	'''
		target = {
			future_price:
			spot_price:
		}

		cosr = {
			future_price:
			spot_price:
		}
	'''

	'''
		config = {
			Openthreshold:
			CloseThreshold:
		}
	'''
	def __init__(self, config):
		self._config = config

	def calc_spread_ratio(self, **kwargs):
		future_price = float(kwargs['target']['future_price'])
		spot_price = float(kwargs['target']['spot_price'])

		return (max(future_price, spot_price)/min(future_price,spot_price)) - 1.

	def calc_profit_rate(self, **kwargs):
		cost_future_price = float(kwargs['cost']['future_price'])
		cost_spot_price = float(kwargs['cost']['spot_price'])

		target_future_price = float(kwargs['target']['future_price'])
		target_spot_price = float(kwargs['target']['future_price'])

		#short future
		if cost_future_price > cost_spot_price:
			profit = (cost_future_price - target_future_price) + (target_spot_price - cost_spot_price)
	
		#long future
		elif cost_future_price < cost_spot_price:
			profit = (target_future_price - cost_future_price) + (cost_spot_price - target_spot_price)
	
		else:
			print('error')
			return -999
		cost = cost_future_price + cost_spot_price

		return profit / cost


	#input target
	def open_signal(self, **kwargs):


		spread = self.calc_spread_ratio(target=kwargs['target'])
		print('(open_signal)The spread is: ', spread*100., '%')

		if spread >= float(self._config['OpenThreshold']):
			return 'open'
		else:
			return 'wait'

	#input target, cost
	def close_signal(self, **kwargs):
		target = kwargs['target']
		cost = kwargs['cost']
		profit_rate = self.calc_profit_rate(target=target, cost=cost)

		print('(close_signal)The spread is: ', spread)
		if profit_rate >= self._config['CloseThreshold']:
			return 'close'
		else:
			return 'wait'

