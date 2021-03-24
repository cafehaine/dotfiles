_RETURN_CODE_COLORS = {
    'error': '{RED}',
    'unknown': '{PURPLE}',
    'success': '{GREEN}'
}

_HOSTNAME_EMOJI_MAP = {
    'galifeu': "🔥",
    'poussifeu': "🐤",
    'kyogre': "💧",
    'kgearch': "🏢",
    'ravenarch': "🏡",
}

def _return_code():
    """
    A prompt field showing the return code of the last command, padded to always
    fit in 3 characters.
    """
    code = '?'
    if __xonsh__.history.rtns:
        code = __xonsh__.history.rtns[-1]
    color = _RETURN_CODE_COLORS['unknown' if code == '?' else ('success' if code == 0 else 'error')]
    padded_code = str(code).center(3)
    return "{}{}{{RESET}}".format(color, padded_code)

def _emoji_hostname():
    if $HOSTNAME not in _HOSTNAME_EMOJI_MAP:
        return "❓"
    return _HOSTNAME_EMOJI_MAP[$HOSTNAME]

$PROMPT_FIELDS['return_code'] = _return_code
$PROMPT_FIELDS['time_format'] = "%H:%M"
$PROMPT_FIELDS['emoji_hostname'] = _emoji_hostname

$PROMPT = '{return_code} {localtime} {YELLOW}{env_name}{BOLD_BLUE}{user}@{emoji_hostname} {BOLD_GREEN}{cwd} {gitstatus}{RESET}\n{prompt_end} '
