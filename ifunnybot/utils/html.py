from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bs4 import BeautifulSoup, Tag


def generate_safe_selector(
    dom: "BeautifulSoup",
):
    """
    Creates a wrapper that returns a function to safely select
    some attribute from an HTML tag and sets the `field` of
    `prop` to it's value.

    Returns false on failure and true on success.
    """
    if dom.css is None:
        raise ReferenceError("dom.css cannot be None")

    def safe_select(selector: str, **kwargs: dict[str, Any]) -> "Tag":
        """
        selector: str - The CSS selector of the element to find.

        Returns true on success, false on failure.
        """
        # checking kwargs
        if kwargs.get("limit", None) is None:
            kwargs["limit"] = 1  # type: ignore

        # getting the element
        elements = dom.css.select(selector, **kwargs)  # type: ignore

        # checking the results
        if len(elements) == 0:
            raise RuntimeError(f"Couldn't find any tags matching: {selector}")

        # unpack
        return elements[0]

    # returning function pointer
    return safe_select
