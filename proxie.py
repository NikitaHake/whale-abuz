import requests
import random

def getProxy(apiKey):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    params = {
        "page": 1,
        "perPage": 10
    }

    url = f"https://api.dashboard.proxy.market/dev-api/v2/packages/{apiKey}"

    try:
        packageId = requests.get(url=url, headers=headers, params=params).json()['data'][0]['id']
    except:
        return Exception("Скорее всего Вы не получили тестовый трафик в сервисе Proxymarket! Пожалуйста, обратитесь в поддержку сервиса Proxymarket с запросом о получении тестового трафика на резидентские прокси!")

    url = f"https://api.dashboard.proxy.market/dev-api/v2/package/countries/{apiKey}"

    countries = requests.get(url=url).json()['data']

    url = f"https://api.dashboard.proxy.market/dev-api/v2/package/create-proxy/{apiKey}"

    payload = {
        "packageId": packageId,
        "country": f"{random.choice(countries)}",
        "rotation": 0
    }

    requests.post(url=url, headers=headers, json=payload)

    url = f"https://api.dashboard.proxy.market/dev-api/list/{apiKey}"

    payload = {
        "type": "all",
        "package_id": packageId,
        "page": 1,
        "page_size": 10,
        "sort": 0
    }

    response = requests.post(url=url, headers=headers, json=payload).json()['list']['data'][0]


    proxy = {
        'http': f'http://{response["login"]}:{response["password"]}@{response["ip"]}:{response["http_port"]}',
        'https': f'http://{response["login"]}:{response["password"]}@{response["ip"]}:{response["http_port"]}'
    }

    return proxy, response