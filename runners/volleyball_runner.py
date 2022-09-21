import contextlib
import datetime as dt
import os
import time

from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_scheduler.classes.runner import BaseRunner
from selenium_scheduler.utils.logging import logger


class VolleyballRunner(BaseRunner):
    # Base config
    conn_max_retries = -1
    max_retries = 5
    exceptions = (
        NoSuchElementException,
        TimeoutException,
        ElementNotInteractableException,
    )
    headless = True
    cache_session = False

    # Custom params
    wd_wait_time = 5
    day_of_week = "Vendredi"
    hour_interval = "17:30-19:00"

    def _close_banner(self) -> None:
        with contextlib.suppress(TimeoutException):
            WebDriverWait(self.driver, self.wd_wait_time).until(
                EC.element_to_be_clickable((By.ID, "cboxClose"))
            ).click()

    def _login(self) -> None:
        self.driver.get("https://sport.unil.ch/?pid=29")
        self._close_banner()
        self.driver.refresh()
        self.driver.find_element(By.NAME, "txtLogin").send_keys(
            os.environ.get("CS_UNIL_USER")
        )
        self.driver.find_element(By.NAME, "txtPassword").send_keys(
            os.environ.get("CS_UNIL_PASS")
        )
        self.driver.find_element(
            By.XPATH, "//button[text()='Connexion']"
        ).click()

    def _book_volleyball_sess(self) -> None:
        self.driver.get("https://sport.unil.ch/?pid=80&aid=58")
        next_date = (dt.datetime.now() + dt.timedelta(days=7)).strftime(
            "%d.%m.%Y"
        )
        items = WebDriverWait(self.driver, self.wd_wait_time).until(
            EC.visibility_of_all_elements_located(
                (By.XPATH, "//div[@class='cours_items']/div[@class='group']")
            )
        )
        for it in items:
            day = it.find_element(By.CLASS_NAME, "day").text
            date = it.find_element(By.CLASS_NAME, "dt").text
            hour = it.find_element(By.CLASS_NAME, "hour").text
            if (
                day == self.day_of_week
                and date == next_date
                and hour == self.hour_interval
            ):
                inscr = it.find_element(By.CLASS_NAME, "inscr").find_element(
                    By.TAG_NAME, "a"
                )
                if url := inscr.get_attribute("href"):
                    self.driver.get(url)
                    self.driver.find_element(
                        By.XPATH,
                        (
                            "//button[@class='btn_insc' "
                            'and text()="s\'inscrire"]'
                        ),
                    ).click()
                    time.sleep(1)
                    self.driver.find_element(
                        By.XPATH,
                        (
                            "//button[@class='shop_cours_info add' "
                            "and text()='Envoyer']"
                        ),
                    ).click()
                    logger.info(
                        "VolleyballRunner: Sucessfully booked next lesson!"
                    )
                    return
        logger.error("VolleyballRunner: Could not find next date...")

    def run(self) -> None:
        self._login()
        self._book_volleyball_sess()
