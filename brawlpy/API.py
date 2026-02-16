class API:
    def __init__(self, version=1) -> None:
        self.BASE = f"https://api.brawlstars.com/v{version}"
        self.PLAYER = self.BASE + "/players/{playerTag}"
        self.CLUB = self.BASE + "/clubs/{clubTag}"
        self.RANKINGS = self.BASE + "/rankings/{countryCode}"
        self.BRAWLERS = self.BASE + "/brawlers"
        self.BRAWLER = self.BASE + "/brawlers/{id}"
        self.EVENTS = self.BASE + "/events/rotation"
