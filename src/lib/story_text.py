"""Plain-text extraction from story data.

Shared by the search indexer (which needs a flat text blob for bi-gram
indexing) and the AI commentary input extractor (which needs readable,
speaker-attributed text for a language model to read).

Note on the data format: spoken text lives in `name` elements, whose
`content` attribute holds the line and `name` attribute holds the speaker.
`Dialog` elements are timing/layout directives and carry no text.
"""
import re
from typing import List, Optional, Set

from ..models.story import Story, StoryElement

# Props that carry no dialog but mark a scene change, mapped to the label used
# in the transcript and the attribute holding the asset name.
_STAGE_DIRECTION_LABELS = {
    "background": ("背景", "image"),
    "image": ("画像", "image"),
    "showitem": ("アイテム", "name"),
}

# Inline markup embedded in dialog text, e.g. "Ave{@nbs}Mujica" for a
# non-breaking space or {@lt} style tags. Stripped for readability.
_INLINE_MARKUP = re.compile(r"\{@[^}]*\}")


def extract_plain_text(story: Story) -> str:
    """Extract all dialog and subtitle text as a single space-joined string.

    This is the flat representation used for search indexing: speaker names
    and dialog are concatenated without structure.

    Args:
        story: Story object

    Returns:
        Space-joined text content
    """
    text_parts = []
    for element in story.story_list:
        text = _element_text(element)
        if text:
            text_parts.append(text)
    return " ".join(text_parts)


def extract_speakers(story: Story) -> Set[str]:
    """Extract the set of unique speaker names appearing in a story.

    Args:
        story: Story object

    Returns:
        Set of speaker names
    """
    speakers = set()
    for element in story.story_list:
        speaker = element.get_speaker()
        if speaker:
            speakers.add(speaker)
    return speakers


def extract_transcript(story: Story) -> List[str]:
    """Extract story text as readable transcript lines.

    Unlike extract_plain_text, this preserves speaker attribution and scene
    boundaries so the result reads as a script. Scene changes appear as ［...］
    markers. Lines are returned without trailing newlines.

    Args:
        story: Story object

    Returns:
        List of transcript lines
    """
    lines: List[str] = []
    current_speaker: Optional[str] = None

    for element in story.story_list:
        prop = element.prop.lower()

        if prop == "name":
            # A 'name' element sets the speaker for the dialog that follows.
            # Some entries also carry inline content, which is spoken text.
            speaker = element.get_speaker()
            if speaker:
                current_speaker = speaker
            content = element.get_text()
            if content:
                lines.append(_format_dialog(current_speaker, content))
        elif prop == "dialog":
            content = element.get_text()
            if content:
                lines.append(_format_dialog(current_speaker, content))
        elif prop == "subtitle":
            subtitle = element.attributes.get("text")
            if subtitle:
                lines.append(f"［字幕］{strip_markup(subtitle)}")
        elif prop == "sticker":
            content = element.attributes.get("text")
            if content:
                lines.append(f"［テロップ］{strip_markup(content)}")
        elif prop in _STAGE_DIRECTION_LABELS:
            # Scene changes: emit a bracketed marker naming the asset
            label, attribute = _STAGE_DIRECTION_LABELS[prop]
            value = element.attributes.get(attribute)
            if value:
                lines.append(f"［{label}: {value}］")
        elif prop == "decision":
            options = element.attributes.get("options")
            if options:
                lines.append(f"［選択肢］{options}")

    return lines


def strip_markup(text: str) -> str:
    """Remove inline markup tags and normalize whitespace in story text.

    Args:
        text: Raw story text

    Returns:
        Cleaned text
    """
    cleaned = _INLINE_MARKUP.sub("", text)
    return " ".join(cleaned.split())


def _element_text(element: StoryElement) -> Optional[str]:
    """Get the reader-facing text of an element, if any."""
    prop = element.prop.lower()
    if prop in ("name", "dialog"):
        return element.get_text()
    if prop == "subtitle":
        return element.attributes.get("text")
    return None


def _format_dialog(speaker: Optional[str], content: str) -> str:
    """Format a dialog line with optional speaker attribution."""
    content = strip_markup(content)
    if speaker:
        return f"{strip_markup(speaker)}: {content}"
    return content
