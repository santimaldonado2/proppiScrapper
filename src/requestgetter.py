from time import sleep
import requests
from lxml.html import fromstring
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('logs/requestgetter.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('|%(asctime)s\t|%(levelname)s\t|%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


class RequestGetter:
    def __init__(self, config):
        self.proxy_list = []
        self.current_proxy = []
        self.proxy_list = []
        self.use_proxy = config['use_proxy'].lower() == "true"
        self.max_attempts = config["max_attempts"]
        self.sleep_time = config["sleep_time"]
        logger.info("Start with configuration: [{}]".format(config))
        print("----------------------")
        print("REQUEST CONFIGURATION:")
        print("use proxy: {}".format(self.use_proxy))
        print("max attempts: {}".format(self.max_attempts))
        print("sleep time: {}".format(self.sleep_time))
        print("----------------------")

    def get_proxies(self):
        logger.info("Start get_proxies")
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = []
        for i in parser.xpath('//tbody/tr')[:10]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.append(proxy)
        self.proxy_list = proxies
        logger.info("End get_proxies :[{}]".format(proxies))

    def get_proxy(self):
        if len(self.proxy_list) == 0:
            self.get_proxies()
        return self.proxy_list.pop()

    def update_current_proxy(self):
        logger.info("Start update_current_proxy")
        if not self.current_proxy:
            self.current_proxy = self.get_proxy()
        logger.info("End update_current_proxy:[{}]".format(self.current_proxy))

    def delete_current_proxy(self):
        logger.info("Start delete_current_proxy")
        self.current_proxy = None
        logger.info("End delete_current_proxy")

    def get_without_proxy(self, url):
        logger.info(f"Start get_without_proxy\t|url={url}")
        response = None
        try:
            response = requests.get(url, timeout=15)
            sleep(self.sleep_time)
            logger.info(f"End get_without_proxy\t|url={url}\t|Response={response}")
        except requests.exceptions.Timeout:
            logger.error(f"Timeout get_without_proxy\t|url={url}")
            sleep(10)
        except Exception as e:
            logger.error(f"Error getting url\t|url={url}\t|Exception={e}")

        return response

    def get_with_proxy(self, url):
        logger.info(f"Start get_with_proxy\t|url={url}")
        attempts = 0
        while attempts < self.max_attempts:
            try:
                self.update_current_proxy()
                response = requests.get(url, proxies={"http": self.current_proxy, "https": self.current_proxy},
                                        timeout=10)
                logger.info(f"End get_without_proxy\t|url={url}\t|Response={response}\t|proxy={self.current_proxy}")
                return response
            except Exception:
                attempts += 1
                self.delete_current_proxy()
                logger.info(f"End get_without_proxy\t|url={url}\t|attempts={attempts}\t|proxy={self.current_proxy}")
        logger.info(f"get_with_proxy reached max attempts, trying without proxy\t|url={url}\t")
        return self.get_without_proxy(url)

    def get(self, url, skip_proxy=False):
        return self.get_with_proxy(url) if self.use_proxy and not skip_proxy else self.get_without_proxy(url)

    def post(self, url, data, headers=None):
        return self.post_with_proxy(url, data, headers) if self.use_proxy else self.post_without_proxy(url, data,
                                                                                                       headers)

    def post_without_proxy(self, url, data, headers=None):
        logger.info(f"Start post_without_proxy\t|url={url}")
        response = None
        try:
            response = requests.post(url,
                                     data=data,
                                     headers=headers,
                                     timeout=10)
            sleep(self.sleep_time)
            logger.info(f"End post_without_proxy\t|url={url}\t|Response={response}\t|data={data}\t|headers={headers}")
        except Exception as e:
            logger.error(f"Error posting url\t|url={url}\t|Exception={e}\t|data={data}\t|headers={headers}")

        return response

    def post_with_proxy(self, url, data, headers=None):
        logger.info(f"Start post_with_proxy\t|url={url}")
        attempts = 0
        while attempts < self.max_attempts:
            try:
                self.update_current_proxy()
                response = requests.post(url,
                                         data=data,
                                         headers=headers,
                                         proxies={"http": self.current_proxy, "https": self.current_proxy},
                                         timeout=10)
                logger.info(f"End post_without_proxy\t|url={url}\t|Response={response}\t|data={data}\t|"
                            f"headers={headers}\t|proxy={self.current_proxy}")
                if not response.ok:
                    raise Exception("Not 200 Exception")
                return response
            except Exception:
                attempts += 1
                logger.error(f"Error posting url\t|url={url}\t|Exception={e}\t|data={data}\t|"
                             f"headers={headers}\t|proxy={self.current_proxy}")
                self.delete_current_proxy()
        logger.info(f"post_with_proxy reached max attempts, trying without proxy\t|url={url}\t")
        return self.post_without_proxy(url, data, headers)
