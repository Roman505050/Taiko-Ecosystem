import requests

def check_proxy(proxy: str | dict, timeout: int = 5) -> bool:
    """
    Checks if the proxy  is working by making a request to http://www.google.com. Proxy only supports http and https

    :param proxy: Proxy in either dict format {'http': 'http://user:pass@ip:port', 'https': 'http://user:pass@ip:port'}
                  or str format 'http://user:pass@ip:port'
    :param timeout: Timeout for proxy check in seconds
    :return: Returns True if the proxy is working, otherwise False
    """
    proxies = {'http': proxy, 'https': proxy} if isinstance(proxy, str) else proxy
    
    try:
        response = requests.get('http://www.google.com', proxies=proxies, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        return False