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
	'OpenThreshold': 0.1*0.01,
	'CloseThreshold': 0.03*0.01,
}

ActionManagerConfig = {
	'FutureThreshold': 0.4,
	'MarginThreshold': 0.4,
}


RobotConfig = {
	'TradeUnitFiat': 30,
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
		spot_price = spot_api.ticker().json()['last']
		future_price = future_api.ticker().json()['last']
		target = {
			'spot_price': spot_price,
			'future_price': future_price,
		}

		print('spot price: ', spot_price)
		print('future_price: ', future_price)
		
		if robot.decide_open(target=target):
			position_manager.show_list()
		else:
			print('wait')

		time.sleep(1)
		
if __name__ == '__main__':
	main()