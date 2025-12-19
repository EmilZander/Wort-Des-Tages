import json
import requests
import subprocess
import schedule
import time
from datetime import datetime

class HtmlScraper:
    class Seperator:
        seperator = ""
        use_left_side = True

        def __init__(self, seperator: str, use_left_side: bool):
            self.seperator = seperator
            self.use_left_side = use_left_side

    url = ""
    seperators = []

    def __init__(self, url: str):
        self.url = url
    
    def html_get(self):
        try:
            response = requests.get(self.url)
        except Exception as e:
            raise Exception(f"Failed to fetch HTML: {e}]")

        return response.text

    def result_get(self):
        try:
            if (len(self.seperators) == 0):
                return self.html_get()
        
            result = self.html_get()

            for sep in self.seperators:
                if sep.seperator in result:
                    parts = result.split(sep.seperator)
                    if len(parts) < 2:
                        continue
                    result = parts[0] if sep.use_left_side else parts[1]
        except Exception as e:
            raise Exception(f"Failed to paarse result: {e}]")
        return result

class Config:
    url = ""
    enabled = False
    sender_phonenumber = ""
    recipent_phonenumbers = []

    def base_url_get(self):
        try:
            if (self.url.find("https://") == -1 and self.url.find("http://") == -1):
                return self.url.split("/")[1]
            return self.url.split("//")[1].split("/")[0] + "/"
        except Exception as e:
            raise Exception(f"Failed to fetch base URL: {e}]")
        
    
    def __init__(self, path):
        self.loadFromJson(path)

    def loadFromJson(self, path: str):
        try:
            with open(path, "r") as file:
                data = json.load(file)

                self.url = data["url"]
                self.enabled = data["enabled"]
                self.sender_phonenumber = data["sender_phonenumber"]
                self.recipent_phonenumbers = data["recipent_phonenumbers"]
        except Exception as e:
            raise Exception(f"Failed to load config from JSON: {e}]")

class SignalMessenger:
    signalCLI_path = "signal-cli"
    sender_number = ""

    def __init__(self, signalCLI_path: str = "signal-cli", sender_number: str = ""):
        self.signalCLI_path = signalCLI_path
        self.sender_number = sender_number

    def is_registered(self) -> bool:
        try:
            result = subprocess.run(
            [self.signalCLI_path, "-u", self.sender_number, "check", self.sender_number],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output = result.stdout.strip()
            error = result.stderr.strip()

            if error:
                print(f"Fehler: {error}")
                return False

            return "true" in output.lower()
        except Exception as e:
            raise Exception(f"Failed to check registration: {e}")
    
    def send_message(self, recipient_numbers: list[str], message: str):
        try:
            for recipient in recipient_numbers:
                subprocess.run(
                    [self.signalCLI_path, "-u", self.sender_number, "send", recipient, "-m", message],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
        except Exception as e:
            raise Exception(f"Failed to send message: {e}")

def run():
    config = Config("config.json")

    if (not config.enabled): return

    word_scraper = HtmlScraper(config.url)

    word_scraper.seperators.append(HtmlScraper.Seperator('href="/rechtschreibung/', False))
    word_scraper.seperators.append(HtmlScraper.Seperator('>', False))
    word_scraper.seperators.append(HtmlScraper.Seperator('<', True))

    url_scraper = HtmlScraper(config.url)
    url_scraper.seperators.append(HtmlScraper.Seperator('<a class="scene__title-link" href="', False))
    url_scraper.seperators.append(HtmlScraper.Seperator('"', True))

    message = f'Das Wort des Tages vom {str(datetime.today().day) + "." + str(datetime.today().month) + "." + str(datetime.today().year)} ist "{word_scraper.result_get().replace("\xad", "")}". \n' + 'Mehr Infos unter: https://{config.base_url_get()}{url_scraper.result_get().replace("\xad", "")}'
    messenger = SignalMessenger(sender_number=config.sender_phonenumber)
    messenger.send_message(config.recipent_phonenumbers, message)

    print(message)

def main():
    schedule.every().day.at("08:00").do(run)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__": 
    main()