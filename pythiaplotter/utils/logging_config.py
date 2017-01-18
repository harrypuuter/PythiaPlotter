"""Setup logging module here

We use a custom formatter which formats different severity levels differently.
"""


import logging


class LevelFormatter(logging.Formatter):
    """Custom message formatter for different severity levels

    Taken from: https://stackoverflow.com/questions/28635679/python-logging-different-formatters-for-the-same-log-file
    """

    def __init__(self, fmt=None, datefmt=None, level_fmts={}):
        """
        fmt is the default format.
        datefmt is the default format for dates.
        level_fmts is a dict where logging levels are the keys,
        and the corresponding values is a format string
        """
        self._level_formatters = {}
        for level, format in level_fmts.items():
            # Could optionally support level names too
            self._level_formatters[level] = logging.Formatter(fmt=format, datefmt=datefmt)
        # self._fmt will be the default format
        super(LevelFormatter, self).__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record):
        if record.levelno in self._level_formatters:
            return self._level_formatters[record.levelno].format(record)

        return super(LevelFormatter, self).format(record)


formatter = LevelFormatter(fmt='%(message)s',
                           level_fmts={logging.ERROR: '%(levelname)s - %(module)s: %(message)s',
                                       logging.WARNING: '%(levelname)s - %(module)s: %(message)s',
                                       logging.INFO: '%(message)s',
                                       logging.DEBUG: '%(levelname)s - %(module)s: %(message)s'})

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
root = logging.getLogger()
root.addHandler(console_handler)
root.setLevel(logging.INFO)