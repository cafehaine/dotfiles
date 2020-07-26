_RETURN_CODE_COLORS = {
    'error': '{RED}',
    'unknown': '{PURPLE}',
    'success': '{GREEN}'
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
    return "{}{}{{NO_COLOR}}".format(color, padded_code)

$PROMPT_FIELDS['return_code'] = _return_code
$PROMPT_FIELDS['time_format'] = "%H:%M"

$PROMPT = '{return_code} {localtime} {YELLOW}{env_name}{BOLD_BLUE}{user}@{hostname} {BOLD_GREEN}{cwd} {gitstatus}{NO_COLOR}\n{prompt_end} '
