"""Image provider base class."""

from abc import ABC, abstractmethod


class ImageProvider(ABC):
    """Image generation provider base class."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        **kwargs,
    ) -> str:
        """Generate an image from text description.

        Args:
            prompt: Text description of the image
            size: Image size (e.g., "1024x1024", "1792x1024")
            **kwargs: Provider-specific parameters

        Returns:
            Image URL
        """
