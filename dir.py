# ==========================================================
# Copyright (c) 2026 Arush
# All Rights Reserved.
#
# Project      : Arush API Telegram Music Bot
# Powered By   : Arush
# Type         : API Based Telegram Music Bot
#
# Bot          : @ArushApibot
# Channel      : https://t.me/arush
# GitHub       : https://github.com/Arush
#
# Unauthorized copying, modification, or redistribution
# of this source code without permission is prohibited.
# ==========================================================
from pathlib import Path

from Elevenyts import logger


def ensure_dirs():
    """
    Create necessary directories if they don't exist.

    Creates:
    - cache/: For temporary cache files
    - downloads/: For downloaded media files
    """
    # List of required directories
    for dir in ["cache", "downloads"]:
        # Create directory (and parents if needed)
        Path(dir).mkdir(parents=True, exist_ok=True)
    logger.info("📁 Cache directories updated.")
