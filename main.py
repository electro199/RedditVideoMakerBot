#!/usr/bin/env python
import math
import sys
import typing
import os
from subprocess import Popen
from typing import Dict, NoReturn, Optional

from prawcore import ResponseException

from reddit.subreddit import get_subreddit_threads
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step, print_substep, format_ordinal
from utils.ffmpeg_install import ffmpeg_install
from utils.id import extract_id
from utils.settings import get_config
from utils.version import check_python, checkversion
from video_creation import (
    chop_background,
    download_background_audio,
    download_background_video,
    get_background_config,
    get_screenshots_of_reddit_posts,
    make_final_video,
)
from video_creation.voices import save_text_to_mp3

__VERSION__ = "4.0.0"

print(
    """
██████╗ ███████╗██████╗ ██████╗ ██╗████████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║       ██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║       ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║███████╗██████╔╝██████╔╝██║   ██║        ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝         ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""
)
print_markdown(
    "### Thanks for using this tool! Feel free to contribute to this project on GitHub! If you have any questions,"
    " feel free to join my Discord server or submit a GitHub issue."
    " You can find solutions to many common problems in the documentation: https://reddit-video-maker-bot.netlify.app/"
)
checkversion(__VERSION__)

reddit_id: Optional[str] = None
reddit_object: Dict[str, str | list]


def make_video(POST_ID: typing.Optional[str] = None) -> None:
    global reddit_id, reddit_object
    reddit_object = get_subreddit_threads(POST_ID)
    reddit_id = extract_id(reddit_object)
    print_substep(f"Thread ID is {reddit_id}", style="bold blue")
    length, number_of_comments = save_text_to_mp3(reddit_object)
    length = math.ceil(length)
    get_screenshots_of_reddit_posts(reddit_object, number_of_comments)
    bg_config = {
        "video": get_background_config("video"),
        "audio": get_background_config("audio"),
    }
    download_background_video(bg_config["video"])
    download_background_audio(bg_config["audio"])
    chop_background(bg_config, length, reddit_object)
    make_final_video(number_of_comments, length, reddit_object, bg_config)


def run_many(times) -> None:
    for x in range(1, times + 1):
        print_step(f"on the {format_ordinal(x)} iteration of {times}")
        make_video()
        Popen("cls" if os.name == "nt" else "clear", shell=True).wait()


def shutdown() -> NoReturn:
    if reddit_id is not None:
        print_markdown("## Clearing temp files")
        cleanup(reddit_id)

    print("Exiting...")
    sys.exit()


def main():
    check_python()
    ffmpeg_install()
    config = get_config()

    try:
        post_ids = config["reddit"]["thread"]["post_id"].split("+")
        if post_ids:
            for index, post_id in enumerate(post_ids):
                index += 1
                print_step(f"on the {format_ordinal(index)} post of {len(post_ids)}")
                make_video(post_id)
                Popen("cls" if os.name == "nt" else "clear", shell=True).wait()
        elif config["settings"]["times_to_run"]:
            run_many(config["settings"]["times_to_run"])
        else:
            make_video()
    except KeyboardInterrupt:
        shutdown()
    except ResponseException:
        print_markdown("## Invalid credentials")
        print_markdown("Please check your credentials in the config.toml file")
        shutdown()
    except Exception as err:
        config["settings"]["tts"]["tiktok_sessionid"] = "REDACTED"
        config["settings"]["tts"]["elevenlabs_api_key"] = "REDACTED"
        config["settings"]["tts"]["openai_api_key"] = "REDACTED"
        print_step(
            f"Sorry, something went wrong with this version! Try again,"
            "and feel free to report this issue at GitHub or the Discord community.\n"
            f"Version: {__VERSION__} \n"
            f"Error: {err} \n"
            f'Config: {config["settings"]}'
        )
        raise err


if __name__ == "__main__":
    main()
