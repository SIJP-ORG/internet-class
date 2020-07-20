import concurrent.futures
import requests
import time
import random

NUM_REQUESTS = 120

REGIST_URL = 'http://name.ninja.fish/register'
REGIST_TIMEOUT = 240

HOSTS_URL = 'http://name.ninja.fish/hosts'
HOSTS_TIMEOUT = 30

'''
Debug info
set http_proxy=127.0.0.1:8888
'''

def request_hosts():
    # adding time distribution across 5 seconds
    sleep_seconds = random.randint(1,5)
    time.sleep(sleep_seconds)

    start1 = time.time()
    with requests.Session() as session:
        adapter = requests.adapters.HTTPAdapter(max_retries=0)
        session.mount('http://', adapter)

    response = requests.get(HOSTS_URL, timeout=HOSTS_TIMEOUT)
    status_code1 = response.status_code
    process1_sec = time.time() - start1

    time.sleep(20)

    start2 = time.time()
    with requests.Session() as session:
        adapter = requests.adapters.HTTPAdapter(max_retries=0)
        session.mount('http://', adapter)

    response = requests.get(HOSTS_URL, timeout=HOSTS_TIMEOUT)
    status_code2 = response.status_code
    process2_sec = time.time() - start2

    return '{0}, {1:.2f}, process1_sec, {2}, {3:.2f}, process2_sec, {4}, init_sleep'.format(
        status_code1, process1_sec, status_code2, process2_sec, sleep_seconds)


def request_registration():
    # adding time distribution across 5 seconds
    sleep_seconds = random.randint(1,5)
    time.sleep(sleep_seconds)

    start = time.time()
    with requests.Session() as session:
        adapter = requests.adapters.HTTPAdapter(max_retries=0)
        session.mount('http://', adapter)

        payload = {
            'ipaddress': '10.1.1.1',
            'hostname': 'z-load-test-{0:05}'.format(random.randint(0,100000))
        }
        response = session.post(REGIST_URL, data=payload, timeout=REGIST_TIMEOUT)
        process_sec = time.time() - start

        error = ''
        if response.status_code == 200:
            for line in response.text.split('\n'):
                if 'error-message' in line:
                    error = '\n' + line
                    break

        return '{0}, {1:.2f}, process_sec, {2}, init_sleep{3}'.format(response.status_code, process_sec, sleep_seconds, error)

def main():
    result_list = []
    random.seed()

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_REQUESTS*3) as executor:
        future_requests = []
        for i in range(0, NUM_REQUESTS):
            future_requests.append(executor.submit(request_registration))
            future_requests.append(executor.submit(request_hosts))

        for future in concurrent.futures.as_completed(future_requests):
            try:
                result = future.result()
            except Exception as e:
                result = 'Test Client Error: {0}: {1}'.format(str(type(e)), e)
            finally:
                result_list.append(result)

    for entry in result_list:
        print(entry)

if __name__ == "__main__":
    main()