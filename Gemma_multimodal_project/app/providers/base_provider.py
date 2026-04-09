from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    def chat_text(self, prompt: str) -> str:
        """Send text-only prompt to model."""
        raise NotImplementedError

    @abstractmethod
    def chat_with_image(self, prompt: str, image_path: str) -> str:
        """Send text + image prompt to model."""
        raise NotImplementedError