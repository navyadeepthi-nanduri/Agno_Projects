from app.providers.openrouter_provider import OpenRouterProvider
from app.providers.base_provider import BaseProvider


class ProviderFactory:
    @staticmethod
    def get_provider(provider_name: str = "openrouter") -> BaseProvider:
        provider_name = provider_name.lower().strip()

        if provider_name == "openrouter":
            return OpenRouterProvider()

        raise ValueError(f"Unsupported provider: {provider_name}")