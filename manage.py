from api.rest import OKCoinFuture, OKCoinSpot
from api import hedge as hedge_action

from position import hedge as hedge_position
from robot import Robot
from strategy.hedge import Hedge  as hedge_strategy

import time

AUTH = {
	'APIKEY':  "61de5afb-aa3d-4ab7-a383-083417c4e088",
	'SECRETKEY': 'CEBE96B1903083EBBD8880EFE8F99484',
	'PASSPHRASE': "jj12345678",
}

URL = 'https://www.okex.com'


#crypt base
FutureOrderConfig = {
	'OrderType': 'market',
	'Pair': 'ETH-USD-181228',
	'Currency': 'ETH',
	'Leverage': '10',
}


#crypt base
SpotOrderConfig = {
	'OrderType': 'market',
	'Pair': 'eth-usdt',
	'MarginTrade': 'True',
	'Currency': 'ETH',

}


StrategyConfig = {
	'OpenThreshold': 0.7*0.01,
	'CloseThreshold': 0.03*0.01,
	'Fee': 0.15*0.01,
}

ActionManagerConfig = {
	'FutureBalanceThreshold': 0.45,
	'MarginRiskThreshold': 1.6,
}


RobotConfig = {
	'TradeUnitFiat': 10,
}
def main():
	#declare api
	spot_api = OKCoinSpot(AUTH, URL, SpotOrderConfig)
	future_api = OKCoinFuture(AUTH, URL, FutureOrderConfig)

	#declare managers

	
	action_manager = hedge_action.Manager(spot_api=spot_api, future_api=future_api, config=ActionManagerConfig)
	position_class = hedge_position.Position
	position_manager = hedge_position.Manager(position_class=position_class)
	strategy = hedge_strategy(config=StrategyConfig)

	robot = Robot(strategy=strategy, action_manager=action_manager, position_manager=position_manager, config=RobotConfig)


	while True:
		try:
			spot_price = spot_api.ticker().json()['last']
			
			future_ticker = future_api.ticker().json() 
			future_price = future_ticker['best_bid']
			target = {
				'spot_price': spot_price,
				'future_price': future_price,
			}

			print('(close)spot price: ', spot_price)
			print('(close)future_price: ', future_price)
		
			position_list = position_manager._position_list
			tmp_list = list()
			if len(position_list) > 0:
				print('checking position_list')
				for position in position_list:
					if robot.decide_close(position=position, target=target):
						print('delete a position')
					else:
						tmp_list.append(position)
				
				position_manager._position_list = tmp_list

				position_manager.show_list()


			target['future_price'] = future_ticker['best_ask']
			print('\n(open) spot_price: ', target['spot_price'])
			print('(open) future_price: ', target['future_price'])
			if robot.decide_open(target=target):
				position_manager.show_list()
			else:
				print('(action)wait')

			print('---------------------------------------------------------------')
			time.sleep(0.125)
		except KeyboardInterrupt:
			print('shut down')	
			break

		except:
			pass


if __name__ == '__main__':
	main()