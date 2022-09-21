import os

from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium_scheduler.classes.runner import BaseRunner
from selenium_scheduler.utils.logging import logger


class MoodleAICCRunner(BaseRunner):
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
    class_options = ["choice_1", "choice_4", "choice_5", "choice_8"]

    def _login(self) -> None:
        self.driver.get("https://moodle.epfl.ch/login/index.php")
        self.driver.find_element(By.ID, "username").send_keys(
            os.environ.get("MOODLE_EPFL_USER")
        )
        self.driver.find_element(By.ID, "password").send_keys(
            os.environ.get("MOODLE_EPFL_PASS")
        )
        self.driver.find_element(By.ID, "loginbutton").click()

    def _book(self) -> None:
        self.driver.get(
            "https://moodle.epfl.ch/mod/choice/view.php?id=1214853"
        )
        found = False
        for opt in self.class_options:
            choice = self.driver.find_element(By.ID, opt)
            disabled = choice.get_attribute("disabled")
            if not disabled:
                choice.click()
                self.driver.find_element(
                    By.XPATH, "//input[@value='Save my choice']"
                ).click()
                found = True
                break
        if found:
            logger.info("MoodleAICCRunner: Successfully booked room!")
        else:
            logger.error("MoodleAICCRunner: Could not book room...")

    def run(self) -> None:
        self._login()
        self._book()
