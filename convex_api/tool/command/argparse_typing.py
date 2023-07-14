from argparse import (
    ArgumentParser,
    Namespace
)
from typing import (
    Any,
    Dict,
    Protocol,
    Union
)

from pydantic import (
    BaseModel,
    Field
)


class SubParsersAction(Protocol):
    @property
    def choices(self) -> Dict[str, ArgumentParser]:
        ...

    def add_parser(self, name: str, **kwargs: Any) -> ArgumentParser:
        ...

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: Any, option_string: Union[str, None] = None) -> None:
        ...


class BaseArgs(BaseModel):
    keyfile: Union[None, str]
    keytext: Union[None, str]
    password: Union[None, str]
    keywords: Union[None, str]
    debug: bool = False
    output_json: bool = Field(alias='json', default=False)
    url: str
