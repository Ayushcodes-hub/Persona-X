import html
import re
from typing import Tuple


INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+(override|prompt|instructions)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(in|a|acting\s+as)", re.IGNORECASE),
    re.compile(r"new\s+operating\s+instructions", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"<\|im_end\|>", re.IGNORECASE),
    re.compile(r"assistant:\s*(system|admin)", re.IGNORECASE),
]


def sanitize_untrusted_content(raw_text: str) -> Tuple[str, bool]:
    """
    Sanitize untrusted web content before passing it to LLM extraction pipelines.
    Strips zero-width control characters, neutralizes injection markers,
    and returns (sanitized_text, injection_detected_flag).
    """
    if not raw_text:
        return "", False

    # 1. Unescape HTML entities
    text = html.unescape(raw_text)

    # 2. Strip zero-width and invisible control characters
    text = re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff]", "", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # 3. Detect known injection triggers
    injection_detected = False
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            injection_detected = True
            # Neutralize the match by replacing with sanitized tag
            text = pattern.sub("[REDACTED_INJECTION_TRIGGER]", text)

    # 4. Collapse excessive whitespace and line breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()

    return text, injection_detected


def wrap_source_for_prompt(source_text: str, source_id: str = "source_1") -> str:
    """
    Wrap untrusted source text in structured XML boundaries with explicit system isolation instructions.
    """
    sanitized, _ = sanitize_untrusted_content(source_text)
    return (
        f'<untrusted_source_content id="{source_id}">\n'
        f'{sanitized}\n'
        f'</untrusted_source_content>'
    )
