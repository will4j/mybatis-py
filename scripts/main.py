import logging.config

import yaml

from settings import LOGGING_CONFIG

logger = logging.getLogger(__name__)

# 初始化日志配置文件
with open(LOGGING_CONFIG, "r") as conf:
    conf_dict = yaml.load(conf, Loader=yaml.FullLoader)
    logging.config.dictConfig(conf_dict)

if __name__ == '__main__':
    logger.info("Hello World")
