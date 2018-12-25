import datetime
import hmac
import base64
import requests
import json


# maybe handle the exception
class HttpHelper:
	def __init__(self, auth, url):
		self.__url = url
		self.__auth = auth

	def buildSign(self, timestamp, method, path, body=''):
		# generate message
		message = str(timestamp) + method+ path + str(body)
		# hash
		mac = hmac.new(bytes(self.__auth['SECRETKEY'], encoding='utf8'), 
			bytes(message, encoding='utf-8'), digestmod='sha256')
		# ecode to base64
		sign = base64.b64encode(mac.digest())
		return sign

	def buildTimestamp(self):
		now = datetime.datetime.utcnow()
		# iso 8601
		timestamp = now.strftime('%Y-%m-%dT%H:%M:%S') + now.strftime('.%f')[:4] + 'Z'
		return timestamp

	def buildHeader(self, method, path, body=''):	
		# build time stamp for timestamp and sign
		timestamp = self.buildTimestamp()
		# build sign
		sign = self.buildSign(timestamp, method, path, body=body)
		header = {
			'Content-Type': 'application/json',
			'OK-ACCESS-KEY': self.__auth['APIKEY'],
			'OK-ACCESS-SIGN': sign,
			'OK-ACCESS-TIMESTAMP': timestamp,
			'OK-ACCESS-PASSPHRASE': self.__auth['PASSPHRASE'],
		}

		return header

	def parse_params_to_str(self, params):
	    url = '?'

	    # the path fot get method
	    for key, value in params.items():
	        url = url + str(key) + '=' + str(value) + '&'

	    return url[0:-1]

	def httpGet(self, path, params=''):

		if params == '':
			# ignore empty params
			pass
		else:
			# actual path = url + path + params
			path = path + self.parse_params_to_str(params)
			
		return requests.get(self.__url + path, headers=self.buildHeader('GET', path))


	def httpPost(self, path, params=''):

		if params != '' or params != {}:
			body = json.dumps(params)
			return requests.post(self.__url + path, data=body, headers=self.buildHeader('POST', path, body=body))
		else:
			return requests.post(self.__url + path, data=body, headers=self.buildHeader('POST', path))





