from loguru import logger
import sys
from pathlib import Path


LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    level='INFO'       
)

logger.add(
    LOG_DIR / 'app.log',
    rotation='10 MB',
    retention='30 days',
    compression='zip',
    level='DEBUG'
)

def get_logger():
    return logger