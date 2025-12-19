import json
import requests

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
        
        return self.url.split("//")[1].split("/")[0]
    
    def __init__(self, path):
        self.loadFromJson(path)

    def loadFromJson(self, path: str):

        with open(path, "r") as file:
            data = json.load(file)

            self.url = data["url"]
            self.enabled = data["enabled"]
            self.sender_phonenumber = data["sender_phonenumber"]
            self.recipent_phonenumbers = data["recipent_phonenumbers"]

def main():
    config = Config("config.json")

    if (not config.enabled):
        return

    scraper = HtmlScraper(config.url)
    scraper.seperators.append(HtmlScraper.Seperator('a class="scene__title-link" href="/rechtschreibung', False))
    scraper.seperators.append(HtmlScraper.Seperator('>', False))
    scraper.seperators.append(HtmlScraper.Seperator('<', True))

    print("Wort des Tages: " + scraper.result_get())

if __name__ == "__main__":
    main()