from ifunnybot.types.post_type import PostType

# CSS selectors for the content of the post
html_selectors = {
    PostType.PICTURE: ["div._3ZEF > img", "src"],
    PostType.VIDEO: ["div._3ZEF > div > video", "data-src"],
    PostType.GIF: ['meta > link[as="image"]', "href"],
}
