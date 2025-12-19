import json
import requests
import subprocess
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
        response = requests.get(self.url)
        return response.text

    def result_get(self):
        if (len(self.seperators) == 0):
            return self.html_get()
        
        result = self.html_get()

        for seperator in self.seperators:
            if seperator.seperator == "" or result.find(seperator.seperator) == -1:
                continue

            result = result.split(seperator.seperator)[0 if seperator.use_left_side else 1]
        
        return result

class Config:
    url = ""
    enabled = False
    sender_phonenumber = ""
    recipent_phonenumbers = []

    def base_url_get(self):
        if (self.url.find("https://") == -1 and self.url.find("http://") == -1):
            return self.url.split("/")[1]
        
        return self.url.split("//")[1].split("/")[0] + "/"
    
    def __init__(self, path):
        self.loadFromJson(path)

    def loadFromJson(self, path: str):

        with open(path, "r") as file:
            data = json.load(file)

            self.url = data["url"]
            self.enabled = data["enabled"]
            self.sender_phonenumber = data["sender_phonenumber"]
            self.recipent_phonenumbers = data["recipent_phonenumbers"]

class SignalMessenger:
    signalCLI_path = "signal-cli"
    sender_number = ""

    def __init__(self, signalCLI_path: str = "signal-cli", sender_number: str = ""):
        self.signalCLI_path = signalCLI_path
        self.sender_number = sender_number

    def is_registered(self) -> bool:
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
    
    def send_message(self, recipient_numbers: list[str], message: str):
        for recipient in recipient_numbers:
            subprocess.run(
                [self.signalCLI_path, "-u", self.sender_number, "send", recipient, "-m", message],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

def main():
    config = Config("config.json")

    if (not config.enabled): return

    word_scraper = HtmlScraper(config.url)

    word_scraper.seperators.append(HtmlScraper.Seperator('href="/rechtschreibung/', False))
    word_scraper.seperators.append(HtmlScraper.Seperator('>', False))
    word_scraper.seperators.append(HtmlScraper.Seperator('<', True))

    url_scraper = HtmlScraper(config.url)
    url_scraper.seperators.append(HtmlScraper.Seperator('<a class="scene__title-link" href="', False))
    url_scraper.seperators.append(HtmlScraper.Seperator('"', True))

    message = f'Das Wort des Tages vom {str(datetime.today().day) + "." + str(datetime.today().month) + "." + str(datetime.today().year)} ist "{word_scraper.result_get().replace("\xad", "")}". \n' + ''
    'Mehr Infos unter: https://{config.base_url_get()}{url_scraper.result_get().replace("\xad", "")}'
    messenger = SignalMessenger(sender_number=config.sender_phonenumber)
    messenger.send_message(config.recipent_phonenumbers, message)

    print(message)

if __name__ == "__main__": main()