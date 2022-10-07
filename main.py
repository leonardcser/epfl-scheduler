import schedule
from dotenv import load_dotenv
from selenium_scheduler import sched, wait

from runners import SimpleVolleyballRunner


def main() -> None:
    load_dotenv()
    sched(SimpleVolleyballRunner(), schedule.every().thursday.at("20:00"))
    wait(sleep_time=60)


if __name__ == "__main__":
    main()
