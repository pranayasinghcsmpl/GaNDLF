import logging
import yaml
from pathlib import Path
from importlib import resources
import colorlog
import tempfile
from GANDLF.utils import get_unique_timestamp


def _flush_to_console():
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "blue",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logging.root.setLevel(logging.DEBUG)
    logging.root.addHandler(console_handler)


def _create_tmp_log_file():
    tmp_dir = Path(tempfile.gettempdir())
    log_dir = Path.joinpath(tmp_dir, ".gandlf")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = Path.joinpath(log_dir, get_unique_timestamp() + ".log")
    _create_log_file(log_file)
    return log_file


def _create_log_file(log_file):
    log_file = Path(log_file)
    log_file.write_text("Starting GaNDLF logging session \n")


def _save_logs_in_file(log_file, config_path):
    with resources.open_text("GANDLF", config_path) as file:
        config_dict = yaml.safe_load(file)
        config_dict["handlers"]["rotatingFileHandler"]["filename"] = str(log_file)
        logging.config.dictConfig(config_dict)


def gandlf_logger_setup(log_file=None, config_path="logging_config.yaml"):
    """
    It sets up the logger. Reads from logging_config.

    Args:
        log_file (str): dir path for saving the logs, defaults to `None`, at which time logs are flushed to console.
        config_path (str): file path for the configuration

    """

    logging.captureWarnings(True)
    try:
        if log_file is None:  # create tmp file
            log_tmp_file = _create_tmp_log_file()
            _save_logs_in_file(log_tmp_file, config_path)
            logging.info(f"The logs are saved in {log_tmp_file}")
        else:  # create the log file
            _create_log_file(log_file)
            _save_logs_in_file(log_file, config_path)
    except Exception as e:
        _flush_to_console()
        logging.error(f"log_file:{e}")
        logging.warning("The logs will be flushed to console")


class InfoOnlyFilter(logging.Filter):
    """
    Display only INFO messages.
    """

    def filter(self, record):
        """
        Determines if the specified record is to be logged.
        Args:
            record (logging.LogRecord): The log record to be evaluated.
        Returns:
            bool: True if the log record should be processed, False otherwise.
        """
        return record.levelno == logging.INFO
