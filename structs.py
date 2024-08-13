import typing
import functools
from pydantic import BaseModel
import pydantic
import pydantic.generics


class Subtitle(BaseModel):
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


class FilteredSubtitle(BaseModel):
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
    rating: float

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class ApiResultFiltSubtitles(BaseModel):
    res: typing.List[FilteredSubtitle]
