import hmac
import base64
from .Httphmacutil import HttpHelper 


class OKCoinSpot(HttpHelper):

	#decide the pair
	def __init__(self, auth, url, order_config):
		super().__init__(auth, url)
		self._order_config = order_config

		'''
		config structure 
		config {
				OrderType: limit/market
				Pair:	eg. btc-usdt
				MarginTrade: True/False
		}
		'''
	def ticker(self):
		pair = self._order_config['Pair']
		print(self._order_config['Pair'])
		PATH = "/api/spot/v3/instruments/{}/ticker".format(pair)

		return self.httpGet(PATH)

	#buy of size is calc by money
	#sell of size is calc by qty
	def place_order(self, **kwargs):
		PATH = '/api/margin/v3/orders'
		side = kwargs['side']
		
		if side == 'sell':
			crypt_amount = kwargs['crypt_amount']
		elif side == 'buy':
			fiat_amount = kwargs['fiat_amount']
		
		order_type = self._order_config['OrderType']
		pair = self._order_config['Pair']
		margin_trade = str(self._order_config['MarginTrade'])

		#Margin Trade?
		if  margin_trade == 'True':
			margin_trading = '2'
		elif margin_trade == 'False':
			margin_trading = '1'

		params = {
			'type': order_type,
			'side': side,
			'instrument_id': pair,
			'margin_trading' : margin_trading
		}

		#limit market have different way in qty to buy
		if order_type == 'limit':
			params['price'] = price
			params['size'] = crypt_amount

		
		elif order_type == 'market':
			if side == 'buy':
				params['notional'] = fiat_amount
			elif kwargs['side'] == 'sell':
				params['size'] = crypt_amount
		

		return self.httpPost(PATH, params=params)

	def find_order(self, order_id):
		PATH = '/api/spot/v3/orders/{}'.format(order_id)
		pair = self._order_config['Pair']
		params = {}
		params['instrument_id'] = pair
		return self.httpGet(PATH, params=params)

	def cancel_order(self, order_id):
		PATH = '/api/spot/v3/cancel_orders/{}'.format(order_id)
		params = {
			'instrument_id': self.__pair,
		}
		return self.httpPost(PATH, params=params)
	
	def get_account(self):
		pair = self._order_config['Pair']
		PATH = '/api/margin/v3/accounts/{}'.format(pair)
		return self.httpGet(PATH)

	def repay_loan(self, currency, amount):
		pair = self._order_config['Pair']
		PATH = '/api/margin/v3/accounts/repayment'

		params = {
			'instrument_id': pair,
			'currency': currency,
			'amount': amount,
		}
		return self.httpPost(PATH, params=params)

	def get_loan_record(self):
		pair = self._order_config['Pair']
		PATH = '/api/margin/v3/accounts/{}/borrowed'.format(pair)
		params = {
			'status': '0',
		}
		return self.httpGet(PATH, params=params)

	def get_margin_account(self):
		pair = self._order_config['Pair']
		PATH = '/api/margin/v3/accounts/{}'.format(pair)
		
		return self.httpGet(PATH)

class OKCoinFuture(HttpHelper):

	#decide the pair

	def __init__(self, auth, url, order_config):
		super().__init__(auth, url)
		self._order_config = order_config
		'''
			config structure 
			config {
				OrderType: limit/market
				Pair:	eg. btu-usdt
				Leverage: 10/20
				SizeUnit: 1 (usd per size)
			}
		'''


	def ticker(self):
		PATH = '/api/futures/v3/instruments/{}/ticker'.format(self._order_config['Pair'])
		return self.httpGet(PATH)

	def get_position(self):
		PATH = '/api/futures/v3/position'
		return self.httpGet(PATH)
	#side, option, fiat_amount, (price if limit)
	def place_order(self, **kwargs):
		print('place future order')
		PATH = '/api/futures/v3/order'

		#vairable redeclare

		#kwargs
		side = kwargs['side']
		option = kwargs['option']
		size = int(kwargs['fiat_amount'] / 10)
		#config
		pair = self._order_config['Pair']
		leverage = self._order_config['Leverage']
		order_type = self._order_config['OrderType']

		#decide order type
		if side == 'open':
		
			if option == 'long':
				position_type = '1'
			elif option == 'short':
				position_type = '2'
		elif side == 'close':
			if option == 'long':
				position_type = '3'
			elif option == 'short':
				position_type = '4'

		#decide match price
		if order_type == 'limit':
			match_price = 0
		elif order_type == 'market':
			match_price = 1

		#build params
		params={
			'instrument_id': pair,
			'type': position_type,
			'size': size,
			'match_price': match_price,
			'leverage': leverage,
		}

		#if limit parse price to params
		if order_type == 'market':
			pass
		elif order_type == 'limit':
			params['price'] = kwargs['price']
		return self.httpPost(PATH, params=params)

	def find_order(self, order_id):
		pair = self._order_config['Pair']
		PATH = '/api/futures/v3/orders/{}/{}'.format(pair, str(order_id))
		return self.httpGet(PATH)

	def cancel_order(self, order_id):
		pair = self._order_config['Pair']
		PATH = '/api/futures/v3/cancel_order/{}/{}'.format(pair, order_id)
		return self.httpPost(PATH)

	def get_transaction(self, order_id):
		pair = self._order_config['Pair']
		PATH = '/api/futures/v3/fills'
		params = {
			'order_id':order_id,
			'instrument_id': pair,
		}
		return self.httpGet(PATH, params=params)


	def get_account(self):
		PATH = '/api/futures/v3/accounts/{}'.format(self._order_config['Currency'])
		return self.httpGet(PATH)
