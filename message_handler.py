import datetime
import logging
import time
import re
import urllib.parse
import html

from  tracker_config import VarType
import announce_parser
import utils
import db
from backend import notify, notify_which_backends, backends_to_string, Backend

logger = logging.getLogger("ANNOUNCE_MANAGER")

def _is_announcement(source, target, tracker_config):
    return (source == tracker_config.announcer_name and
        target == tracker_config.irc_channel)

def _sanitize_message(message):
    message = utils.strip_irc_color_codes(message)
    message = html.unescape(message)
    return message


@db.db_session
def on_message(tracker_config, source, target, message):
    if not _is_announcement(source, target, tracker_config):
        logger.debug("Message is no announcement")
        return

    message = _sanitize_message(message)

    announcement = announce_parser.parse(tracker_config, message)
    if announcement is None:
        return

    backends = notify_which_backends(tracker_config, announcement.category)
    backends_string = backends_to_string(backends)

    if tracker_config.delay > 0:
        logger.debug("{}: Waiting %s seconds to notify %s",
                tracker_config.short_name, tracker_config.delay, announcement.torrent_name)
        time.sleep(tracker_config.delay)

    db.Announced(date=datetime.datetime.now(), title=announcement.torrent_name,
            indexer=tracker_config.short_name, torrent=announcement.torrent_url, pvr=backends_string)
    logger.info("Notifying %s of release from %s: %s", backends_string,
                tracker_config.short_name, announcement.torrent_name)

    backend = notify(announcement, backends, tracker_config.short_name)

    if backend is None:
        # TODO Print rejection reason
        logger.debug("Release was rejected: %s", announcement.torrent_name)
    else:
        logger.info("%s approved release: %s", backend, announcement.torrent_name)
        snatched = db.Snatched(date=datetime.datetime.now(), title=announcement.torrent_name,
                indexer=tracker_config.short_name, torrent=announcement.torrent_url, pvr=backend)
