from PIL import ImageTk


class ManagedImage(ImageTk.PhotoImage):
    """
    A PhotoImage subclass that registers instances to prevent premature
    garbage collection. Uses a strong reference registry to ensure persistence.
    """

    _registry = {}  # <-- strong reference now

    def __init__(self, image=None, name=None, **kwargs):
        super().__init__(image=image, **kwargs)
        self._image_id = name or id(self)
        ManagedImage._registry[self._image_id] = self

    @classmethod
    def get(cls, key):
        """
        Get an image from the registry by key.

        Args:
            key: The identifier of the image.

        Returns:
            ManagedPhotoImage or None
        """
        return cls._registry.get(key)

    @classmethod
    def clear_registry(cls):
        """
        Clear the image registry.
        """
        cls._registry.clear()

    def __repr__(self):
        return f"<ManagedPhotoImage id={self._image_id} width={self.width()} height={self.height()}>"
