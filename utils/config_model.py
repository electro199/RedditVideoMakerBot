from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field, StringConstraints


class RedditCreds(BaseModel):
    client_id: Annotated[
        str,
        StringConstraints(
            min_length=12, max_length=30, pattern=r"^[-a-zA-Z0-9._~+/]+=*$"
        ),
    ] = Field(..., description="The ID of your Reddit app of SCRIPT type")

    client_secret: Annotated[
        str,
        StringConstraints(
            min_length=20, max_length=40, pattern=r"^[-a-zA-Z0-9._~+/]+=*$"
        ),
    ] = Field(..., description="The SECRET of your Reddit app of SCRIPT type")

    username: Annotated[
        str, StringConstraints(min_length=3, max_length=20, pattern=r"^[-_0-9a-zA-Z]+$")
    ] = Field(..., description="The username of your Reddit account")

    password: Annotated[str, StringConstraints(min_length=8)] = Field(
        ..., description="The password of your Reddit account"
    )

    twofa: Optional[bool] = Field(False, description="Whether Reddit 2FA is enabled")


class RedditThread(BaseModel):
    random: Optional[bool] = Field(
        False, description="If true, picks a random thread instead of asking for URL"
    )

    subreddit: Annotated[
        str, StringConstraints(min_length=3, max_length=20, pattern=r"[_0-9a-zA-Z\+]+$")
    ] = Field(..., description="Name(s) of subreddit(s), '+' separated")

    post_id: Annotated[Optional[str], StringConstraints(pattern=r"^[+a-zA-Z0-9]*$")] = (
        Field("", description="Specify a Reddit post ID if desired")
    )

    max_comment_length: Annotated[int, Field(ge=10, le=10000)] = Field(
        500, description="Max number of characters per comment"
    )

    min_comment_length: Annotated[int, Field(ge=0, le=10000)] = Field(
        1, description="Min number of characters per comment"
    )

    post_lang: Optional[str] = Field(
        "", description="Target language code for translation (e.g., 'es-cr')"
    )

    min_comments: Annotated[int, Field(ge=10)] = Field(
        20, description="Minimum number of comments required"
    )


class RedditThreadExtras(BaseModel):
    min_comments: Annotated[
        int,
        Field(
            default=20,
            ge=10,
            le=999999,
            description="The minimum number of comments a post should have to be included. Default is 20.",
            examples=[29],
        ),
    ]


class AIConfig(BaseModel):
    ai_similarity_enabled: Annotated[
        bool,
        Field(
            default=False,
            description="Threads read from Reddit are sorted based on their similarity to the keywords given below.",
        ),
    ]
    ai_similarity_keywords: Annotated[
        str,
        Field(
            default="",
            description="Every keyword or sentence, separated by commas, is used to sort Reddit threads based on similarity.",
            examples=["Elon Musk, Twitter, Stocks"],
        ),
    ]


class SettingsTTS(BaseModel):
    voice_choice: Annotated[
        Literal[
            "elevenlabs",
            "streamlabspolly",
            "tiktok",
            "googletranslate",
            "awspolly",
            "pyttsx",
        ],
        Field(
            default="tiktok",
            description="The voice platform used for TTS generation.",
            examples=["tiktok"],
        ),
    ]
    random_voice: Annotated[
        bool,
        Field(
            default=True,
            description="Randomizes the voice used for each comment.",
            examples=[True],
        ),
    ]
    elevenlabs_voice_name: Annotated[
        Literal[
            "Adam", "Antoni", "Arnold", "Bella", "Domi", "Elli", "Josh", "Rachel", "Sam"
        ],
        Field(
            default="Bella",
            description="The voice used for ElevenLabs.",
            examples=["Bella"],
        ),
    ]
    elevenlabs_api_key: Annotated[
        str,
        Field(
            default="",
            description="ElevenLabs API key.",
            examples=["21f13f91f54d741e2ae27d2ab1b99d59"],
        ),
    ]
    aws_polly_voice: Annotated[
        str,
        Field(
            default="Matthew",
            description="The voice used for AWS Polly.",
            examples=["Matthew"],
        ),
    ]
    streamlabs_polly_voice: Annotated[
        str,
        Field(
            default="Matthew",
            description="The voice used for Streamlabs Polly.",
            examples=["Matthew"],
        ),
    ]
    tiktok_voice: Annotated[
        str,
        Field(
            default="en_us_001",
            description="The voice used for TikTok TTS.",
            examples=["en_us_006"],
        ),
    ]
    tiktok_sessionid: Annotated[
        str,
        Field(
            default="",
            description="TikTok sessionid needed for TikTok TTS.",
            examples=["c76bcc3a7625abcc27b508c7db457ff1"],
        ),
    ]
    python_voice: Annotated[
        str,
        Field(
            default="1",
            description="The index of the system TTS voices (starts from 0).",
            examples=["1"],
        ),
    ]
    py_voice_num: Annotated[
        str,
        Field(
            default="2",
            description="The number of system voices available.",
            examples=["2"],
        ),
    ]
    silence_duration: Annotated[
        float,
        Field(
            default=0.3,
            description="Time in seconds between TTS comments.",
            examples=["0.1"],
        ),
    ]
    no_emojis: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to remove emojis from the comments.",
            examples=[False],
        ),
    ]
    openai_api_url: Annotated[
        str,
        Field(
            default="https://api.openai.com/v1/",
            description="The API endpoint URL for OpenAI TTS generation.",
            examples=["https://api.openai.com/v1/"],
        ),
    ]
    openai_api_key: Annotated[
        str,
        Field(
            default="",
            description="Your OpenAI API key for TTS generation.",
            examples=["sk-abc123def456..."],
        ),
    ]
    openai_voice_name: Annotated[
        Literal[
            "alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"
        ],
        Field(
            default="alloy",
            description="The voice used for OpenAI TTS generation.",
            examples=["alloy"],
        ),
    ]
    openai_model: Annotated[
        Literal["tts-1", "tts-1-hd"],
        Field(
            default="tts-1",
            description="The model variant used for OpenAI TTS generation.",
            examples=["tts-1"],
        ),
    ]


class SettingsBackground(BaseModel):
    background_video: Annotated[
        str,
        Field(
            default="minecraft",
            description="Sets the background for the video based on game name",
            examples=["rocket-league"],
        ),
        StringConstraints(strip_whitespace=True),
    ] = "minecraft"

    background_audio: Annotated[
        str,
        Field(
            default="lofi",
            description="Sets the background audio for the video",
            examples=["chill-summer"],
        ),
        StringConstraints(strip_whitespace=True),
    ] = "lofi"

    background_audio_volume: Annotated[
        float,
        Field(
            default=0.15,
            ge=0,
            le=1,
            description="Sets the volume of the background audio. If you don't want background audio, set it to 0.",
            examples=[0.05],
        ),
    ] = 0.15

    enable_extra_audio: Annotated[
        bool,
        Field(
            default=False,
            description="Used if you want to render another video without background audio in a separate folder",
        ),
    ] = False

    background_thumbnail: Annotated[
        bool,
        Field(
            default=False,
            description="Generate a thumbnail for the video (put a thumbnail.png file in the assets/backgrounds directory.)",
        ),
    ] = False

    background_thumbnail_font_family: Annotated[
        str,
        Field(
            default="arial",
            description="Font family for the thumbnail text",
            examples=["arial"],
        ),
    ] = "arial"

    background_thumbnail_font_size: Annotated[
        int,
        Field(
            default=96,
            description="Font size in pixels for the thumbnail text",
            examples=[96],
        ),
    ] = 96

    background_thumbnail_font_color: Annotated[
        str,
        Field(
            default="255,255,255",
            description="Font color in RGB format for the thumbnail text",
            examples=["255,255,255"],
        ),
    ] = "255,255,255"


class Settings(BaseModel):
    allow_nsfw: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to allow NSFW content. True or False.",
            examples=[False],
        ),
    ]
    theme: Annotated[
        Literal["dark", "light", "transparent"],
        Field(
            default="dark",
            description="Sets the Reddit theme. For story mode, 'transparent' is also allowed.",
            examples=["light"],
        ),
    ]
    times_to_run: Annotated[
        int,
        Field(
            default=1,
            ge=1,
            description="Used if you want to run multiple times. Must be an int >= 1.",
            examples=[2],
        ),
    ]
    opacity: Annotated[
        float,
        Field(
            default=0.9,
            ge=0.0,
            le=1.0,
            description="Sets the opacity of comments when overlaid over the background.",
            examples=[0.8],
        ),
    ]
    storymode: Annotated[
        bool,
        Field(
            default=False,
            description="Only read out title and post content. Great for story-based subreddits.",
            examples=[False],
        ),
    ]
    storymodemethod: Annotated[
        Literal[0, 1],
        Field(
            default=1,
            description="Style used for story mode: 0 = static image, 1 = fancy video.",
            examples=[1],
        ),
    ]
    storymode_max_length: Annotated[
        int,
        Field(
            default=1000,
            ge=1,
            description="Max length (in characters) of the story mode video.",
            examples=[1000],
        ),
    ]
    resolution_w: Annotated[
        int,
        Field(
            default=1080,
            description="Sets the width in pixels of the final video.",
            examples=[1440],
        ),
    ]
    resolution_h: Annotated[
        int,
        Field(
            default=1920,
            description="Sets the height in pixels of the final video.",
            examples=[2560],
        ),
    ]
    zoom: Annotated[
        float,
        Field(
            default=1.0,
            ge=0.1,
            le=2.0,
            description="Sets the browser zoom level. Useful for making text larger.",
            examples=[1.1],
        ),
    ]
    channel_name: Annotated[
        str,
        Field(
            default="Reddit Tales",
            description="Sets the channel name for the video.",
            examples=["Reddit Stories"],
        ),
    ]
    tts: SettingsTTS
    background: SettingsBackground


class Reddit(BaseModel):
    creds: RedditCreds
    thread: RedditThread


class Config(BaseModel):
    reddit: Reddit
    ai: AIConfig
    settings: Settings
