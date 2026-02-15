from typing import TYPE_CHECKING, Callable, Concatenate, Any

from ifunnybot.types.parsing_exception import ParsingError

if TYPE_CHECKING:
    from bs4 import BeautifulSoup, Tag


def generate_safe_selector(
    dom: "BeautifulSoup",
) -> Callable[Concatenate[str, ...], "Tag"]: # type: ignore
    """
    Creates a wrapper around the BeautifulSoup implementation
    if CSS selectors.

    Basically, pass in a selector find it within the HTML. If it
    was found, return the HTML element that the selector finds,
    otherwise, raise a `ParsingError` which must be caught.
    """

    if dom.css is None:
        raise ReferenceError("dom.css cannot be None")

    def safe_select(selector: str, **kwargs: dict[str, Any]) -> "Tag":
        """
        selector: str - The CSS selector of the element to find.

        Returns a `Tag` on success, otherwise, raise a `ParsingError`.
        """
        # checking kwargs
        if kwargs.get("limit", None) is None:
            kwargs["limit"] = 1  # type: ignore

        # getting the element
        elements = dom.css.select(selector, **kwargs)  # type: ignore

        # checking the results
        if len(elements) == 0:
            raise ParsingError(f"Couldn't find any tags matching: {selector}")

        # unpack
        return elements[0]

    # returning function pointer
    return safe_select
