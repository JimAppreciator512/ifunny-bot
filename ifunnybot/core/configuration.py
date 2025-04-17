class Configuration:
    """
    This class represents all the configuration options for the bot.
    """

    # writing data
    PICKLE_LOCATION = "pickles"

    # logging
    LOG_LOCATION = "logs"

    # default image format
    IMAGE_FORMAT = "PNG"

    def __init__(
        self,
        pickle_location: str = PICKLE_LOCATION,
        log_location: str = LOG_LOCATION,
        image_format: str = IMAGE_FORMAT,
    ):
        self.pickle_location = pickle_location
        self.log_location = log_location
        self.image_format = image_format

    def __repr__(self) -> str:
        return f"<Configuration: log_location={self.log_location}, pickle_location={self.pickle_location}, image_format={self.image_format}>"
