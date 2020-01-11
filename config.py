import profig
import logging

cfg = None
base_sections = [ "webui", "log", "sonarr", "radarr", "lidarr" ]
logger = logging.getLogger("CONFIG")

def init():
    global cfg
    global base_sections
    if cfg is not None:
        return cfg

    cfg = profig.Config('settings.cfg')
    cfg.read()

    # Settings
    cfg.init('webui.host', 'localhost')
    cfg.init('webui.port', '3467')
    cfg.init('webui.user', 'admin')
    cfg.init('webui.pass', 'password')

    cfg.init('log.to_file', True)
    cfg.init('log.to_console', True)

    cfg.init('sonarr.apikey', None, type=str)
    cfg.init('sonarr.url', 'http://localhost:8989')

    cfg.init('radarr.apikey', None, type=str)
    cfg.init('radarr.url', 'http://localhost:7878')

    cfg.init('lidarr.apikey', None, type=str)
    cfg.init('lidarr.url', 'http://localhost:8686')

    for section in cfg.sections():
        if section.name in base_sections:
            continue
        # Init mandatory tracker values
        section.init('nick', None, type=str)

        # Init optional tracker values
        section.init('irc_port', 6667)
        section.init('tls', False)
        section.init('tls_verify', False)
        section.init('nick_pass', None, type=str)
        section.init('inviter', None, type=str)
        section.init('invite_cmd', None, type=str)
        section.init('delay', 0)
        section.init('notify_sonarr', False)
        section.init('notify_radarr', False)
        section.init('notify_lidarr', False)


    #for s in cfg.sections():
    #    print(s)
    return cfg

mandatory_tracker_fields = [ "nick" ]

def validate_config():
    global cfg
    global tracker_fields
    valid = True

    if not (cfg.get("sonarr.apikey") or
            cfg.get("radarr.apikey") or
            cfg.get("lidarr.apikey")):
        logger.error("Must specify at least one backend (Sonarr/Radarr/Lidarr)")
        valid = False

    for section in cfg.sections():
        if section.name in base_sections:
            continue

        for mandatory in mandatory_tracker_fields:
            if not section.get(mandatory):
                logger.error("{}: Must set '{}'".format(section.name, mandatory))
                valid = False

        if bool(section.get("inviter")) != bool(section.get("invite_cmd")):
            logger.error("{}: Must set both 'inviter' and 'invite_cmd'".format(section.name))
            valid = False

    for section in cfg:
        if len(str(cfg[section])) == 0:
            logger.error("{}: Empty value in configuration not allowed".format(section))
            valid = False
    return valid
