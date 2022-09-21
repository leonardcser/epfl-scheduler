import schedule
from dotenv import load_dotenv
from selenium_scheduler import sched, wait

from runners import MoodleAICCRunner, VolleyballRunner


def main() -> None:
    load_dotenv()
    sched(VolleyballRunner(), schedule.every().friday.at("08:01"))
    sched(MoodleAICCRunner(), schedule.every().tuesday.at("18:01"))
    wait(sleep_time=20)


if __name__ == "__main__":
    main()
