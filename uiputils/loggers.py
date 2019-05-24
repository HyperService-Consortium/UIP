
import logging.handlers


class AddressFileLogger(logging.Logger):
    def __init__(self, logname, log_dir, level=logging.INFO):
        super().__init__(logname, level)
        self.handle = logging.handlers.TimedRotatingFileHandler(
            log_dir,
            encoding="utf-8",
            when="H",
            interval=1,
            backupCount=10
        )
        self.handle.setFormatter(logging.Formatter('%(asctime)-15s %(name)s %(addr)8s %(message)s'))
        self.handle.setLevel(logging.INFO)
        self.handle.suffix = "%Y-%m-%d_%H_%M.log"
        self.addHandler(self.handle)


def console_logger_init():
    """
    to shield
    """
    formatter = logging.Formatter('%(asctime)-15s %(name)s %(message)s')
    console_logger.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    console_handler.suffix = "%Y-%m-%d_%H.log"
    console_logger.addHandler(console_handler)


console_logger = logging.getLogger('console_logger')
console_handler = logging.StreamHandler()
console_logger_init()
