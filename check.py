import random
import re
from time import sleep
import requests
import json
from btcaddr import Wallet
from time import sleep
from fake_user_agent import user_agent

request_timeout = 30

proxy_services_list = [
	"PrivateKeeper",
]

proxy_types = ["http", "https", "socks4", "socks5"]

proxy_services_api_tokens = {}
proxies_list = {
	"PrivateKeeper": [],
}
not_working_proxies_counter = {
	"PrivateKeeper": 0,
}


def set_request_timeout(timeout):
	global request_timeout

	request_timeout = timeout


def add_proxy_service_token(proxy_service, api_token):
	proxy_services_api_tokens[proxy_service] = api_token


def private_keeper_handler(proxy_types_list=None):
	if not proxy_types_list:
		proxy_types_list = proxy_types
	url = "https://pk.community/v2/proxylist.txt?key=%s&type=%s" % (proxy_services_api_tokens["PrivateKeeper"], ",".join(proxy_types_list))
	response = requests.get(url)
	if response.status_code == 200:
		# Удаляем html теги
		text = re.sub(r"<[^>]+>", "", response.text, flags=re.S)
		text = text.split("\r\n")
		for proxy_string in text:
			# Получаемая строка прокси 127.0.0.1:80|HTTP
			if "|" in proxy_string:
				proxy_string = proxy_string.split("|")
				proxy_string[1] = proxy_string[1].lower()
				proxies_list["PrivateKeeper"].append(proxy_string)


def initialize_proxy_services():
	for proxy_service_name, api_token in proxy_services_api_tokens.items():
		if proxy_service_name == "PrivateKeeper":
			private_keeper_handler()



def generate_addresses(count):
	addresses = {}
	for i in range(count):
		wallet = Wallet()
		pub = wallet.address.__dict__["mainnet"].__dict__["pubaddr1"]
		prv = wallet.key.__dict__["mainnet"].__dict__["wif"]
		addresses[pub] = prv
	return addresses


def check_balance_btc(data=generate_addresses(100)):
	proxy_service = proxy_services_list[random.randint(0, len(proxy_services_list) - 1)]
	proxy_string, proxy_protocol = proxies_list[proxy_service][random.randint(0, len(proxies_list[proxy_service]) - 1)]

	try:
		addresses = "|".join(data.keys())
		headers = {
			"User-Agent": user_agent()
		}
		url = f"https://blockchain.info/multiaddr?active={addresses}"
		proxies = {
			"http": "%s://%s" % (proxy_protocol, proxy_string),
			"https": "%s://%s" % (proxy_protocol, proxy_string),
		}
		response = requests.get(url, headers=headers, proxies=proxies, timeout=request_timeout, verify=False).json()
		sleep(0.5)
		extract = []
		for address in response["addresses"]:
			# add all data into a list
			extract.append({
				"address": address["address"],
				"balance": address["final_balance"],
				"private": data[address["address"]]
			})
		return extract
	except Exception as e:
		print(e)
		return []


"""def last_seen_bc(address):

	try:
		address = address
		reading_state = 1
		while reading_state:
			try:
				htmlfile = urlopen(
					f"https://blockchain.info/q/addressfirstseen/{address}?format=json",
					timeout=10,
				)
				htmltext = htmlfile.read().decode("utf-8")
				reading_state = 0
			except:
				reading_state += 1
				sleep(60 * reading_state)
		ts = int(htmltext)
		if ts == 0:
			return 0
		return str(datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))
	except:
		return None
"""