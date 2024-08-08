from dataclasses import dataclass
import typing
import functools


class Subtitle:
    """
    ### Attributes

    begin : str
        The time at which the subtitle begins.
    end : str
        The time at which the subtitle ends.
    text : str
        The text of the subtitle.
    """

    begin: str
    end: str
    text: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class FilteredSubtitle:
    """
    ### Attributes
    rating: float
        The relevance of the subtitle to the topic (0-1).
    begin : str
        The time at which the subtitle begins.
    end : str
        The time at which the subtitle ends.
    text : str
        The text of the subtitle.
    """

    begin: str
    end: str
    text: str
    rating: float = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
