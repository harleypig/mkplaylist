"""
Query parser for mkplaylist.

This module provides a parser for natural language-like criteria strings.
"""

# Starfleet Protocols
import re
import logging

from typing import Any
from typing import Dict
from typing import List
from datetime import datetime
from datetime import timedelta

logger = logging.getLogger(__name__)


class QueryParser:

    """Parser for natural language-like criteria strings."""

    def __init__(self):
        """Initialize the query parser."""
        # Define regex patterns for different criteria
        self.patterns = {
            "recently_added": re.compile(
                r"(\d+)\s+(?:most\s+)?recently\s+added\s+songs"
            ),
            "last_played": re.compile(
                r"(\d+)\s+(?:most\s+)?(?:recently\s+played|last\s+played)\s+songs"
            ),
            "most_played": re.compile(r"(\d+)\s+most\s+played\s+songs"),
            "artist": re.compile(r"songs\s+by\s+(.+?)(?:\s+and|\s*$)"),
            "album": re.compile(r"songs\s+from\s+(.+?)(?:\s+and|\s*$)"),
            "genre": re.compile(r"songs\s+in\s+(.+?)(?:\s+and|\s*$)"),
            "added_days": re.compile(r"songs\s+added\s+in\s+the\s+last\s+(\d+)\s+days"),
            "played_days": re.compile(
                r"songs\s+played\s+in\s+the\s+last\s+(\d+)\s+days"
            ),
        }

    def parse(self, criteria_string: str) -> Dict[str, Any]:
        """
        Parse a criteria string into a dictionary of criteria.

        Args:
            criteria_string: Natural language-like criteria string

        Returns:
            Dictionary of criteria
        """
        logger.info(f"Parsing criteria: {criteria_string}")

        # Check if there are multiple criteria
        if " and " in criteria_string.lower():
            # Split by 'and' and parse each part
            parts = criteria_string.lower().split(" and ")
            combined_criteria = []

            for part in parts:
                part = part.strip()
                if part:
                    sub_criteria = self._parse_single_criteria(part)
                    if sub_criteria:
                        combined_criteria.append(sub_criteria)

            if combined_criteria:
                return {"combined_criteria": combined_criteria}
            else:
                logger.warning(f"Could not parse any criteria from: {criteria_string}")
                return {}
        else:
            # Single criteria
            return self._parse_single_criteria(criteria_string.lower())

    def _parse_single_criteria(self, criteria_string: str) -> Dict[str, Any]:
        """
        Parse a single criteria string.

        Args:
            criteria_string: Single criteria string

        Returns:
            Dictionary of criteria
        """
        # Try each pattern
        for pattern_name, pattern in self.patterns.items():
            match = pattern.search(criteria_string)
            if match:
                return self._build_criteria(pattern_name, match)

        logger.warning(f"Could not parse criteria: {criteria_string}")
        return {}

    def _build_criteria(self, pattern_name: str, match: re.Match) -> Dict[str, Any]:
        """
        Build criteria dictionary from a regex match.

        Args:
            pattern_name: Name of the matched pattern
            match: Regex match object

        Returns:
            Dictionary of criteria
        """
        if pattern_name == "recently_added":
            limit = int(match.group(1))
            return {
                "sort_by": "added_at",
                "sort_order": "desc",
                "limit": limit,
            }

        elif pattern_name == "last_played":
            limit = int(match.group(1))
            return {
                "sort_by": "last_played_at",
                "sort_order": "desc",
                "limit": limit,
            }

        elif pattern_name == "most_played":
            limit = int(match.group(1))
            return {
                "sort_by": "play_count",
                "sort_order": "desc",
                "limit": limit,
            }

        elif pattern_name == "artist":
            artist = match.group(1).strip()
            return {
                "artist": artist,
            }

        elif pattern_name == "album":
            album = match.group(1).strip()
            return {
                "album": album,
            }

        elif pattern_name == "genre":
            genre = match.group(1).strip()
            return {
                "genre": genre,
            }

        elif pattern_name == "added_days":
            days = int(match.group(1))
            added_after = datetime.now() - timedelta(days=days)
            return {
                "added_after": added_after,
                "sort_by": "added_at",
                "sort_order": "desc",
            }

        elif pattern_name == "played_days":
            days = int(match.group(1))
            played_after = datetime.now() - timedelta(days=days)
            return {
                "played_after": played_after,
                "sort_by": "last_played_at",
                "sort_order": "desc",
            }

        return {}

    def get_supported_patterns(self) -> List[str]:
        """
        Get a list of supported criteria patterns.

        Returns:
            List of pattern descriptions
        """
        return [
            "X most recently added songs",
            "X last played songs",
            "X most played songs",
            "songs by ARTIST",
            "songs from ALBUM",
            "songs in GENRE",
            "songs added in the last X days",
            "songs played in the last X days",
        ]
