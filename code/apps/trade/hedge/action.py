from ....resources.api.rest import OKCoinFuture, OKCoinSpot
from ....resources.api import hedge as hedge_action

from ....resources.position import hedge as hedge_position
from ....resources.strategy.hedge import Hedge  as hedge_strategy

from ....test.verbose import vprint

from robot import Robot


import os
import time
import configparser
import pkg_resources

def start_trading(root_dir):


	setting_path = os.path.join(root_dir, 'config/setting.conf')
	trading_path = os.path.join(root_dir, 'config/apps/trade/hedge.conf')
	
	
	#load setting
	setting_config = configparser.ConfigParser()

	setting_config.read(setting_path)
	
	URL = setting_config['URL']['okex']
	AUTH = dict(setting_config['AUTH'])


	#load trading config
	trading_config = configparser.ConfigParser()
	
	trading_config.read(trading_path)
	vprint('(trading)load trading config')

	SpotOrderConfig = dict(trading_config['SpotOrder'])
	FutureOrderConfig = dict(trading_config['FutureOrder'])
	ActionManagerConfig = dict(trading_config['ActionManager'])
	StrategyConfig = dict(trading_config['Strategy'])
	RobotConfig = dict(trading_config['Robot'])
	
	
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

			vprint('(close)spot price: ', spot_price)
			vprint('(close)future_price: ', future_price)
		
			position_list = position_manager._position_list
			tmp_list = list()
			if len(position_list) > 0:
				vprint('checking position_list')
				for position in position_list:
					if robot.decide_close(position=position, target=target):
						vprint('delete a position')
					else:
						tmp_list.append(position)
				
				position_manager._position_list = tmp_list

				position_manager.show_list()


			target['future_price'] = future_ticker['best_ask']
			vprint('(open) spot_price: ', target['spot_price'])
			vprint('(open) future_price: ', target['future_price'])
			if robot.decide_open(target=target):
				position_manager.show_list()
			else:
				vprint('(action)wait')

			vprint('split line')
			time.sleep(0.125)
		except KeyboardInterrupt:
			vprint('shut down')	
			break
		except:
			pass

		
		