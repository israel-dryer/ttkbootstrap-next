from PIL import Image

from ttkbootstrap_next.images.photo import Photo


def create_transparent_image(width: int, height: int) -> "Photo":
    """
    Create a fully transparent PIL image of the given size.
    """
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    pm = Photo(image=img)
    return pm
