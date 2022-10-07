import datetime as dt
import os

import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium_scheduler.classes.runner import BaseRunner
from selenium_scheduler.utils.logging import logger


class SimpleVolleyballRunner(BaseRunner):
    # Base config
    conn_max_retries = -1
    max_retries = 5
    exceptions = tuple()
    use_webdriver = False
    headless = True
    cache_session = False

    # Custom params
    PID = 80
    RID_BASE = 253064
    WEEK_NO_BASE = 40

    DOMAIN = "https://sport.unil.ch"
    STATUS_XPATH = "//*[@id='inscriptions']/div[1]/dl[2]/dd[2]/button"

    def __init__(self) -> None:
        self.session = requests.Session()

    def _parse_content(self, content: bytes) -> etree.HTML:
        soup = BeautifulSoup(content, "html.parser")
        return etree.HTML(str(soup))

    def _login_session(self) -> None:
        form_data = {
            "txtLogin": os.environ.get("CS_UNIL_USER"),
            "txtPassword": os.environ.get("CS_UNIL_PASS"),
        }
        self.session.post(
            f"{self.DOMAIN}/cms_core/auth/login/return/pid=29", data=form_data
        )

    def _get_booking_status(self, rid: int) -> str:
        res = self.session.get(
            f"{self.DOMAIN}/?pid={self.PID}&rid={rid}#inscription"
        )
        dom = self._parse_content(res.content)
        print(dom.xpath(self.STATUS_XPATH))
        return (dom.xpath(self.STATUS_XPATH)[0].text or "").strip()

    def _book_next_date(self, rid: int) -> None:
        # TODO: Make rid dynamic...
        # For this, still need to figure out how it works.
        # Does it update every week, or is it fixed and predefined for
        # the future? An what are the ranges?
        self.session.post(
            f"{self.DOMAIN}/?pid={self.PID}&rid={rid}#form",
            data={"confirm_valid": 1, "groupe_nom": "", "type": 1},
        )

    def _get_rid(self) -> int:
        week_no_now = dt.datetime.now().isocalendar()[1]
        return (week_no_now - self.WEEK_NO_BASE) + self.RID_BASE

    def run(self) -> None:
        self._login_session()
        rid = self._get_rid()
        status = self._get_booking_status(rid).lower()
        if status == "complet":
            logger.info(f"{rid} is already full")
        elif status == "supprimer l'inscription":
            logger.info(f"{rid} booking already confirmed!")
        else:
            self._book_next_date(rid)
            logger.info("Successfully booked!!!")
