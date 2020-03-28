import re
import requests
import time
import json
import sys
from bs4 import BeautifulSoup as BS


class User:
	def __init__(self, username, password, post_link, token):
		self.username = username
		self.password = password
		self.token = token
		self.like_url = post_link
		self.session = requests.Session()
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
			'Accept': '*/*',
			'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
			'Accept-Encoding': 'gzip, deflate, br',
			'Connection': 'keep-alive'
		}

		self.payload = {
			'email': self.username,
			'pass': self.password
		}
		self.login_url = 'https://vk.com/'

		self.owner_id = None
		self.item_id = None

	def login(self):
		try:
			page = self.session.get('https://m.vk.com/login')
			soup = BS(page.content, 'lxml')
			url = soup.find('form')['action']
			response = self.session.post(url, data=self.payload, headers=self.headers)
	
			soup = BS(response.content, 'lxml')
			userName = soup.select('a[class=op_owner]')
			
			if not userName:
				raise KeyError
		except (KeyError, BaseException) as e:
			print("Shit happend. Login fail.", e)
			sys.exit()
		else:
			print(f'Successfully login as: {userName[0]["data-name"]}')
		  
	def __repr__(self):
		return "User('{}', '{}', '{}', '{}')".format(self.username, self.password, self.post_link, self.token)

	def __str__(self):
		return '{} - {} - {} - {}'.format(self.username, self.password, self.post_link, self.token)


def get_token(username, password):
    client_id = 2274003
    client_secret = 'hHbZxrka2uZ6jB1inYsH'

    url = f'https://oauth.vk.com/token?grant_type=password&client_id={client_id}&client_secret={client_secret}&username={username}&password={password}&v=5.103&2fa_supported=1'
    try:
        response = requests.get(url).json()
        token = response['access_token']
        return token
    except KeyError as err:
        print(f'Didn`t get: {err.args[0]}')
        if (response['error']):
            print(f"Reason: {response['error_description']}")
            sys.exit()
    except ConnectionError as err:
        print("Connection error")

def get_data_from_link(link_to_search):
	try:
		base = (re.findall('wall(.+)_(\\d+)', link_to_search))
	except IndexError as e:
		print(f"Invalid url! {e}")
	except Exception as e:
		print(e)
	else:
		return base[0]

def read_data():
    data = {}
    try:
        with open('data.txt', 'r+') as json_file:
            data = json.load(json_file)
        return data
    except KeyError as e:
        if e.args[0] in ['link', 'login', 'password', 'token']:
            print(f'Cannot find: {e.args[0]}')
    except IOError as e:
        print(e)


def main():
	hole_data = read_data()

	link, username, password = [key for key in hole_data.values()]
	token = get_token(username, password)
	print(link)
	owner_id, item_id = get_data_from_link(link)
	print(owner_id, item_id)

	user = User(username, password, link, token)
	print(f'Ur VK token:{user.token}', end='\n\n')
	user.login()
	
	session = user.session
	
		  
	users = None
	while True:
		users = []
		try:
			req_likes = requests.get(
                f'https://api.vk.com/method/likes.getList?access_token={token}&type=post&owner_id={owner_id}&item_id={item_id}&v=5.103').json()
			if 'response' in req_likes:
				if req_likes['response']['count'] != 0:
					print(req_likes)
					users = req_likes['response']['items']
			elif 'error' in req_likes:
				return req_likes

		except KeyError as error:
			print(error)
			print(req_likes)

       
		for user in users:
			data = {
				'act': 'spam',
				'al': '1',
				'mid': user,
				'object': 'wall' + str(owner_id) + '_' + str(item_id)
			}

			response = session.post('https://vk.com/like.php',
										 data=data)
			res = re.findall('hash: \'(?:[a-zA-Z]|[0-9])+', str(response.text))[0]
			res = res.replace('hash: \'', '')
			user_hash = res.replace('"', '')

			data = {
				'act': 'do_spam',
				'al': '1',
				'hash': user_hash,
				'mid': user,
				'object': 'wall' + str(owner_id) + '_' + str(item_id)
			}

			session.post('https://vk.com/like.php',
							  data=data)
			print(f'{user} - banned')
		for user in users:
			response = requests.get(f'https://api.vk.com/method/account.unban?access_token={token}&owner_id={user}&v=5.103').json()
			print(response)
			time.sleep(0.4)
		time.sleep(1.3)


if __name__ == '__main__':
    main()
