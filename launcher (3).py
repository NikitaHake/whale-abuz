import threading
import subprocess
import json
import time

def load_api_keys():
    try:
        with open("apis.json", "r") as f:
            ...
    except (FileNotFoundError, json.JSONDecodeError):
        twocaptcha = input("Введите API-ключ для 2captcha: ")
        proxymarket = input("Введите API-ключ для proxymarket: ")
        keys = {'twocaptcha': twocaptcha, 'proxymarket': proxymarket}
        with open("apis.json", "w") as f:
            json.dump(keys, f)

def run_program(thread_index):
    print(f"Запуск потока {thread_index}")
    command = ["python", "main.py"]
    subprocess.run(command)

def main():
    load_api_keys()
    num_threads = int(input("Введите количество потоков: "))
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=run_program, args=(i + 1,))
        threads.append(thread)
        thread.start()
        time.sleep(5)
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()