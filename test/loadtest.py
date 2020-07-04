import concurrent.futures
import requests
import time
import random

NUM_REQUESTS = 100

TIMEOUT = 20

REGIST_URL = 'http://name3.ninja.fish/register'
REGIST_TIMEOUT = 240

'''
Debug info
set http_proxy=127.0.0.1:8888
'''

def load_url(url, timeout):
    ans = requests.head(url, timeout=timeout)
    return ans.status_code

def request_registration():
    # adding time distribution across 10 seconds
    sleep_seconds = random.randint(1,10)
    time.sleep(sleep_seconds)

    start = time.time()
    with requests.Session() as session:
        adapter = requests.adapters.HTTPAdapter(max_retries=0, pool_connections=100)
        session.mount('http://', adapter)

        payload = {
            'ipaddress': '10.1.1.1',
            'hostname': 'load-test-{0:05}'.format(random.randint(0,100000))
        }
        response = session.post(REGIST_URL, data=payload, timeout=REGIST_TIMEOUT)
        process_sec = time.time() - start

        error = ''
        if response.status_code == 200 and 'error-message' in response.text:
            error = '\n' + response.text

        return '{0}, {1:.2f}, process_sec, {2}, init_sleep{3}'.format(response.status_code, process_sec, sleep_seconds, error)

def main():
    result_list = []
    random.seed()

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_REQUESTS) as executor:
        future_to_url = []
        for i in range(0, NUM_REQUESTS):
            future_to_url.append(executor.submit(request_registration))

        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
            except Exception as e:
                data = 'Test Client Error: {0}: {1}'.format(str(type(e)), e)
            finally:
                result_list.append(data)

    for entry in result_list:
        print(entry)

if __name__ == "__main__":
    main()