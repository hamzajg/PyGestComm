"""Phone numbers are identifiers, so they are stored as canonical text.

Canonical form is an optional leading ``+`` followed by digits only: the
separators users type (spaces, dots, dashes, slashes, parentheses) are
stripped, so one number has exactly one representation and a plain string
search finds it. An empty string means "no phone".

See ``specs/contact-phone-format/SPEC.md`` decisions D1 (canonical storage),
D2 (integer-era payloads and the legacy ``0``) and D3 (validation strength).
"""

import re

_SEPARATOR = re.compile(r"[\s.\-/()]")
_CANONICAL = re.compile(r"^\+?[0-9]{4,20}$")


def _strip_separators(text):
    """Drop the separators users type, keeping a leading ``+`` in place."""
    if text.startswith("+"):
        return "+" + _SEPARATOR.sub("", text[1:])
    return _SEPARATOR.sub("", text)


def canonical_phone(value):
    """Return the canonical form of ``value`` or raise ``ValueError``.

    ``None``, an empty string and the legacy ``0`` all mean "no phone" and
    canonicalise to ``''``. Numeric payloads from the deployed client are
    accepted and stringified. Anything that is not an optional ``+`` plus 4 to
    20 digits (after separator stripping) is rejected.
    """
    if value is None:
        return ""
    text = str(value).strip()
    if text == "0":
        text = ""
    if not text:
        return ""
    digits = _strip_separators(text)
    if not _CANONICAL.match(digits):
        raise ValueError("not a phone number: %r" % (value,))
    return digits


def searchable_phone(term):
    """The canonical digits of a free-text term, or ``''`` when it is not one.

    Lets the assistant match a search such as ``06 12 34 56 78`` against the
    stored canonical value without guessing which separators were typed.
    """
    digits = _strip_separators((term or "").strip())
    return digits if _CANONICAL.match(digits) else ""
