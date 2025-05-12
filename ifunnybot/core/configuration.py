from ifunnybot.types.mode import ImageFormat

class Configuration:
    """
    This class represents all the configuration options for the bot.
    """

    # writing data
    PICKLE_LOCATION = "pickles"

    # logging
    LOG_LOCATION = "logs"

    # default image format
    IMAGE_FORMAT: ImageFormat = ImageFormat.PNG

    # preference to return the url of a video and not embed the file,
    # this saves on performance
    PREFER_VIDEO_URL: bool = True

    def __init__(
        self,
        pickle_location: str = PICKLE_LOCATION,
        log_location: str = LOG_LOCATION,
        image_format: ImageFormat = IMAGE_FORMAT,
        prefer_video_url: bool = PREFER_VIDEO_URL
    ):
        self.pickle_location = pickle_location
        self.log_location = log_location
        self.image_format = image_format
        self.prefer_video_url = prefer_video_url

    def __repr__(self) -> str:
        return f"<Configuration: log_location={self.log_location}, pickle_location={self.pickle_location}, image_format={self.image_format.name}, prefer_video_url={self.prefer_video_url}>"
