class Robot:

	def __init__(self, **kwargs):
		#logic of robot
		self._strategy = kwargs['strategy']

		#what robot involve
		#decide how robot involve
		self._action_manager = kwargs['action_manager']
		self._position_manager = kwargs['position_manager']
		self._config = kwargs['config']

	#input target
	def decide_open(self, **kwargs):
		
		#
		

		#redeclare some variables

		#target price
		target = kwargs['target']
		strategy = self._strategy
		action_manager = self._action_manager
		position_manager = self._position_manager

		#logic
		signal = strategy.open_signal(target=target)

		
		if not self._action_manager.safe():
			print('(decide_open) Balance not safe')
			return False


		if signal == 'open':
			#check enough money to trade
		
			trade_detail = action_manager.open(future_fiat_amount=self._config['TradeUnitFiat'], target=target)
			if trade_detail:
				position_manager.add(detail=trade_detail)	
				return True
		
		return False

	#input position, target,
	def decide_close(self, **kwargs):
		#redeclare variables
		strategy = self._strategy
		action_manager = self._action_manager
		position_manager = self._position_manager


		position = kwargs['position']
		cost = position.cost()
		target = kwargs['target']
		print('(decide_close)future buying price: ', position.future['price'])
		print('(decide_close)margin buying price: ', position.margin['price'])
		signal = strategy.close_signal(target=target, cost=cost)

		if signal == 'close':
			trade_detail = action_manager.close(position=position, target=target)
			if trade_detail:
				return True

		return False


