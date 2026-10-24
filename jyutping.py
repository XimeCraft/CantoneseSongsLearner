# ------------------------------------------------------------------
#  Jyutping syllables
#  -- Split a syllable (without tone) into initial and final
#  -- Orders follow the standard LSHK Jyutping tables
# ------------------------------------------------------------------

INITIALS = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'ng', 'h',
            'gw', 'kw', 'w', 'z', 'c', 's', 'j']

FINALS = [
    'aa', 'aai', 'aau', 'aam', 'aan', 'aang', 'aap', 'aat', 'aak',
    'a', 'ai', 'au', 'am', 'an', 'ang', 'ap', 'at', 'ak',
    'e', 'ei', 'eu', 'em', 'en', 'eng', 'ep', 'et', 'ek',
    'i', 'iu', 'im', 'in', 'ing', 'ip', 'it', 'ik',
    'o', 'oi', 'ou', 'on', 'ong', 'ot', 'ok',
    'u', 'ui', 'un', 'ung', 'ut', 'uk',
    'oe', 'oeng', 'oet', 'oek',
    'eoi', 'eon', 'eot',
    'yu', 'yun', 'yut',
    'm', 'ng',                    # syllabic nasals: 唔 m, 五 ng
]

_INITIAL_ORDER = {x: n for n, x in enumerate(INITIALS)}
_FINAL_ORDER = {x: n for n, x in enumerate(FINALS)}

# Longest first, so 'gw' is tried before 'g' and 'ng' before 'n'
_BY_LENGTH = sorted(INITIALS, key=len, reverse=True)


def split(syllable):
    """Return (initial, final); initial is '' for a zero initial.
    Returns None when the syllable isn't valid Jyutping.
    """
    s = syllable.strip('()~ ').lower()

    for initial in _BY_LENGTH:
        if s.startswith(initial) and s[len(initial):] in _FINAL_ORDER:
            return initial, s[len(initial):]

    if s in _FINAL_ORDER:
        return '', s

    return None


def sort_key(initial, final):
    """Table order; zero initial after the others, unknown parts last."""
    return (_INITIAL_ORDER.get(initial, len(INITIALS) if initial == '' else len(INITIALS) + 1),
            _FINAL_ORDER.get(final, len(FINALS)))
