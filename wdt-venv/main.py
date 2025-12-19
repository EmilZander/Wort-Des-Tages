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
    

def main():
    scraper = HtmlScraper("https://www.duden.de/wort-des-tages")
    scraper.seperators.append(HtmlScraper.Seperator('a class="scene__title-link" href="/rechtschreibung', False))
    scraper.seperators.append(HtmlScraper.Seperator('>', False))
    scraper.seperators.append(HtmlScraper.Seperator('<', True))

    print("Wort des Tages: " + scraper.result_get())

if __name__ == "__main__":
    main()