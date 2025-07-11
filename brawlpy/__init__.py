"""
Brawl Stars API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~
A basic wrapper for the Brawl Stars API.
:copyright: (c) 2022-Present PyStarr
:license: MIT, see LICENSE for more details.
"""

from .API import API
from .main import Client
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

__all__ = [
    "API",
    "Client",
    "Player",
    "Club",
    "ClubMember",
    "ClubRanking",
    "PlayerRanking",
    "BrawlerRanking",
    "Event",
    "Brawler",
    "PlayerBrawler",
    "Gadget",
    "StarPower",
    "Gear",
]

__title__ = "brawlpy"
__author__ = "PyStarr"
__license__ = "MIT"
__copyright__ = "Copyright 2022-Present PyStarr"
__version__ = "1.3.0"
