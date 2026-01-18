from xml.dom import NotFoundErr

from .API import API
from .errors import (
    Forbidden,
    TagNotFoundError,
    RateLimitError,
    UnexpectedError,
    ServerError,
    BrawlerNotFound,
    CountryNotFound,
)
from .utils import checkTag

import aiohttp
from .objects import (
    Player,
    Club,
    ClubMember,
    ClubRanking,
    PlayerRanking,
    BrawlerRanking,
    Event,
    Brawler,
    PlayerBrawler,
    Gadget,
    StarPower,
    Gear,
)


class Client:
    def __init__(self, token):
        self.TOKEN = token
        self.api = API()
        self.headers = {"Authorization": f"Bearer {token}"}
        self.session = None

    async def initialize(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def close(self):
        if self.session:
            await self.session.close()

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def request(self, url, method="GET", **kwargs):
        if self.session is None:
            raise RuntimeError(
                "Session not initialized. Call await client.initialize()"
            )

        async with self.session.request(method, url, **kwargs) as resp:
            status = resp.status
            try:
                data = await resp.json()
            except aiohttp.ContentTypeError:
                data = await resp.text()
            return data, status

    async def get_player(self, tag):
        """Get a player by tag"""

        Tag = checkTag(tag)

        url = self.api.PLAYER.format(playerTag=Tag)

        player, status = await self.request(url)
        if 300 > status >= 200:
            c = player["club"]
            if len(c) < 1:
                cl = None
            else:
                cl = await self.get_club(c["tag"])

            brs = player["brawlers"]
            brrs = []
            for each in brs:
                grs = []
                srs = []
                gears = []
                for i in each["gadgets"]:
                    gr = Gadget(i["name"], i["id"])
                    grs.append(gr)
                for i in each["starPowers"]:
                    sr = StarPower(i["name"], i["id"])
                    srs.append(sr)
                for i in each["gears"]:
                    gear = Gear(i["name"], i["id"], i["level"])
                    gears.append(gear)

                br = PlayerBrawler(
                    each["name"],
                    each["id"],
                    each["power"],
                    each["rank"],
                    each["trophies"],
                    each["highestTrophies"],
                    grs,
                    gears,
                    srs,
                )
                brrs.append(br)

            Pl = Player(
                player["name"],
                player["tag"],
                player["icon"]["id"],
                player["trophies"],
                player["expLevel"],
                player["expPoints"],
                cl,
                player["highestTrophies"],
                player["soloVictories"],
                player["duoVictories"],
                player["3vs3Victories"],
                player["bestRoboRumbleTime"],
                player["bestTimeAsBigBrawler"],
                brrs,
            )

            return Pl

        elif status == 403:
            raise Forbidden(status, url, player["message"])
        elif status == 404:
            raise TagNotFoundError(status)
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, "")
        elif status == 503:
            raise ServerError(status, url)

    async def get_battle_log(self, tag):
        """Get a Player's battle log by there tag"""

        Tag = checkTag(tag)

        url = self.api.PLAYER.format(playerTag=Tag) + "/battlelog"

        log, status = await self.request(url)
        if 300 > status >= 200:
            return log["items"]
        elif status == 403:
            raise Forbidden(status, url, log["message"])
        elif status == 404:
            raise TagNotFoundError(status)
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, "")
        elif status == 503:
            raise ServerError(status, url)

    async def get_club(self, tag):
        """Get a club by tag"""

        Tag = checkTag(tag)
        url = self.api.CLUB.format(clubTag=Tag)
        club, status = await self.request(url)

        if 300 > status >= 200:
            cc_members = []
            for each in club["members"]:
                m = ClubMember(
                    each["name"],
                    each["icon"]["id"],
                    each["tag"],
                    each["role"],
                    each["nameColor"],
                    each["trophies"],
                )
                cc_members.append(m)

            try:
                dsc = club["description"]
            except KeyError:
                dsc = None

            cl = Club(
                club["tag"],
                club["name"],
                dsc,
                club["type"],
                club["badgeId"],
                club["requiredTrophies"],
                club["trophies"],
                cc_members,
            )

            return cl

        elif status == 403:
            raise Forbidden(status, url, club["message"])
        elif status == 404:
            raise TagNotFoundError(status)
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, club)
        elif status == 503:
            raise ServerError(status, url)

    async def brawlers(self):
        """Get a list of all the brawlers currently in the game"""

        url = self.api.BRAWLERS
        brawlers, status = await self.request(url)
        if 300 > status >= 200:
            brss = brawlers["items"]
            brs = []
            for b in brss:
                gadgets = []
                srs = []

                for each in b["gadgets"]:
                    gr = Gadget(each["name"], each["id"])
                    gadgets.append(gr)

                for each in b["starPowers"]:
                    sr = StarPower(each["name"], each["id"])
                    srs.append(sr)

                brs.append(Brawler(b["name"], b["id"], srs, gadgets))

            return brs
        elif status == 403:
            raise Forbidden(status, url, brawlers["message"])
        elif status == 404:
            raise BrawlerNotFound(status)
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, "")
        elif status == 503:
            raise ServerError(status, url)

    async def events(self):
        """Get the list of all the events currently in rotation"""

        url = self.api.EVENTS

        events, status = await self.request(url)

        if 300 > status >= 200:
            event_list = []

            for each in events:
                event = Event(
                    each["event"]["id"],
                    each["event"]["mode"],
                    each["event"]["map"],
                    each["startTime"],
                    each["endTime"],
                )

                event_list.append(event)

            return event_list

        elif status == 403:
            raise Forbidden(status, url, events["message"])
        elif status == 404:
            raise NotFoundErr(status, "Not Found!")
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, "")
        elif status == 503:
            raise ServerError(status, url)

    async def get_players_rankings(self, countryCode="global", limit=None):
        """Get top players rankings"""

        url = self.api.RANKINGS.format(countryCode=countryCode) + "/players"

        if limit:
            url += "?limit={}".format(limit)

        rankings, status = await self.request(url)

        if 300 > status >= 200:
            rankgs = []

            for each in rankings["items"]:
                try:
                    cl = each["club"]
                except KeyError:
                    cl = None
                else:
                    cl = cl["name"]
                rankgs.append(
                    PlayerRanking(
                        each["name"],
                        each["tag"],
                        each["nameColor"],
                        each["icon"]["id"],
                        each["trophies"],
                        each["rank"],
                        cl,
                    )
                )

            return rankgs

        elif status == 403:
            raise Forbidden(status, url, rankings["message"])
        elif status == 404:
            raise NotFoundErr(status, "Not Found!")
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, "")
        elif status == 503:
            raise ServerError(status, url)

    async def get_brawlers_rankings(self, brawlerID, countryCode="global", limit=None):
        """Get top rankings based on brawlers"""

        url = self.api.RANKINGS.format(countryCode=countryCode) + "/brawlers/{}".format(
            brawlerID
        )

        if limit:
            url += "?limit={}".format(limit)

        rankings, status = await self.request(url)

        if 300 > status >= 200:
            rankgs = []

            for each in rankings["items"]:
                try:
                    cl = each["club"]
                except KeyError:
                    cl = None
                else:
                    cl = cl["name"]
                rankgs.append(
                    BrawlerRanking(
                        "",
                        each["tag"],
                        each["name"],
                        each["nameColor"],
                        each["icon"]["id"],
                        each["trophies"],
                        each["rank"],
                        cl,
                    )
                )

            return rankgs

        elif status == 403:
            raise Forbidden(status, url, rankings["message"])
        elif status == 404:
            raise BrawlerNotFound(status, brawlerID)
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, "")
        elif status == 503:
            raise ServerError(status, url)

    async def get_club_rankings(self, countryCode="global", limit=None):
        """Get top clubs rankings"""

        url = self.api.RANKINGS.format(countryCode=countryCode) + "/clubs"

        if limit:
            url += "?limit={}".format(limit)

        rankings, status = await self.request(url)

        if 300 > status >= 200:
            clubs = []

            for each in rankings["items"]:
                clubs.append(
                    ClubRanking(
                        each["tag"],
                        each["name"],
                        each["badgeId"],
                        each["trophies"],
                        each["rank"],
                        each["memberCount"],
                    )
                )

            return clubs

        elif status == 403:
            raise Forbidden(status, url, rankings["message"])
        elif status == 404:
            raise CountryNotFound(status, countryCode)
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, "")
        elif status == 503:
            raise ServerError(status, url)

    async def get_club_members(self, clubTag):
        """Get members of a club"""

        tag = checkTag(clubTag)

        url = self.api.CLUB.format(clubTag=tag) + "/members"

        club, status = await self.request(url)

        if 300 > status >= 200:
            cc_members = []
            for each in club["items"]:
                m = ClubMember(
                    each["name"],
                    each["icon"]["id"],
                    each["tag"],
                    each["role"],
                    each["nameColor"],
                    each["trophies"],
                )
                cc_members.append(m)

            return cc_members

        elif status == 403:
            raise Forbidden(status, url, club["message"])
        elif status == 404:
            raise TagNotFoundError(status)
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, "")
        elif status == 503:
            raise ServerError(status, url)

    async def get_brawler_byID(self, brawlerID: int):
        """Get A brawler by id"""

        url = self.api.BRAWLER.format(id=brawlerID)

        b, status = await self.request(url)

        if 300 > status >= 200:
            gadgets = []
            srs = []

            for each in b["gadgets"]:
                gr = Gadget(each["name"], each["id"])
                gadgets.append(gr)

            for each in b["starPowers"]:
                sr = StarPower(each["name"], each["id"])
                srs.append(sr)

            br = Brawler(b["name"], b["id"], srs, gadgets)

            return br

        elif status == 403:
            raise Forbidden(status, url, b["message"])
        elif status == 404:
            raise BrawlerNotFound(status, id=brawlerID)
        elif status == 429:
            raise RateLimitError(status, url)
        elif status == 500:
            raise UnexpectedError(status, url, b)
        elif status == 503:
            raise ServerError(status, url)

    async def get_brawler_byName(client, name):
        """Get a brawler by its name"""

        brawlers = await client.brawlers()

        for br in brawlers:
            if br.name.lower() == name.lower():
                return br
