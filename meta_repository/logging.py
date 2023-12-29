import inspect
import logging
import os
import re
from logging.config import BaseConfigurator

from loguru import logger

# _global_loguru_format may be changed by LoguruInterceptHandler
_global_loguru_format = os.getenv(
    "LOGURU_FORMAT",
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)


def compact_name_format(record) -> str:
    """ loguru dynamic formatter

    :param record: log record
    :return:
    """
    compact_name = compact_path(record["name"])

    def format_name(match):
        return match.group().format_map({"name": compact_name})

    return re.sub(r"{name(:.*?)?}", format_name, _global_loguru_format) + "\n{exception}"


class LoguruInterceptHandler(logging.Handler):
    """intercept standard logging messages toward loguru

    https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
    """

    def __init__(self, loguru_config: dict = None, loguru_format: str = None):
        super().__init__()
        self.loguru_config = loguru_config
        if loguru_format:
            global _global_loguru_format
            _global_loguru_format = loguru_format
        self.configure_loguru()

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    def configure_loguru(self):
        LoguruDictConfigurator(self.loguru_config).configure()


class LoguruDictConfigurator(BaseConfigurator):
    value_converters = {
        "ext": "ext_convert",
        "cfg": "cfg_convert",
        "lambda": "lambda_convert",
    }

    # https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.configure
    def configure(self):
        loguru_config = {}
        config = self.config

        # list of dict
        if "handlers" in config:
            handlers_config = config.get("handlers", [])
            handlers = []
            for handler_dict in handlers_config:
                _handler = self.configure_handler(handler_dict)
                handlers.append(_handler)
            if handlers:
                loguru_config["handlers"] = handlers

        # list of dict
        if "levels" in config:
            loguru_config["levels"] = config["levels"]

        # dict
        if "extra" in config:
            loguru_config["extra"] = config["extra"]

        # callable
        if "patcher" in config:
            _patcher = config["patcher"]
            loguru_config["patcher"] = self.resolve(_patcher)

        # list of tuple
        if "activation" in config:
            activation_config = config.get("activation", [])
            activations = []
            for activation_dict in activation_config:
                _activation = self.configure_activation(activation_dict)
                activations.append(_activation)
            if activations:
                loguru_config["activation"] = activations

        logger.configure(**loguru_config)  # type: ignore

    def configure_handler(self, config: dict) -> dict:
        # https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
        handler = {}

        _sink = config.pop("sink", None)
        handler["sink"] = self.convert(_sink)

        _format = config.pop("format", None)
        if _format:
            handler["format"] = self.convert(_format)
        else:
            handler["format"] = _global_loguru_format

        _filter = config.pop("filter", None)
        if _filter:
            handler["filter"] = self.convert(_filter)

        # rest config use as it is
        handler.update(config)
        return handler

    def configure_activation(self, config: dict) -> tuple:
        if len(config) != 1:
            raise ValueError('Unable to configure activation, should only have one item per element but got '
                             '%r' % config)
        key, value = config.popitem()
        return key, value

    def convert(self, value):
        if not isinstance(value, str):
            return value
        m = self.CONVERT_PATTERN.match(value)
        if m:
            d = m.groupdict()
            prefix = d['prefix']
            converter = self.value_converters.get(prefix, None)
            if converter:
                suffix = d['suffix']
                converter = getattr(self, converter)
                value = converter(suffix)
        return value

    def lambda_convert(self, value):
        """Default converter for the lambda:// protocol."""
        return eval("lambda " + value)


def compact_path(path: str, retain=2) -> str:
    """通过压缩路径前缀简化路径输出

    :param path: 原始路径，如：infrastructure.adapters.socketio.namespaces
    :param retain: 保留层级，默认2
    :return: 前缀缩写后的路径，如：i.a.s.namespaces.teach_namespace
    """
    if not path or retain < 1 or path.count(".") < retain:
        return path

    slices = path.split(".")
    # i.a.s.namespaces.teach_namespace
    return ".".join([s[0] for s in slices[:-retain] if s]) + "." + ".".join(slices[-retain:])
