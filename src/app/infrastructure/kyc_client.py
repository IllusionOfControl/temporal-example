import httpx


class KYCClientError(Exception):
    """KYC client exception"""


class KYCClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def verify_kyc(self, user_id: str, name: str) -> str:
        try:
            payload = {"user_id": user_id, "name": name}
            response = await self.client.post(self.base_url, json=payload)

            if response.status_code >= 500:
                raise KYCClientError(f"KYC API error: {response.status_code}")

            response.raise_for_status()
            return response.json()["status"]
        except httpx.RequestError as e:
            raise KYCClientError(f"Network error: {e!s}") from e

    async def close(self):
        await self.client.aclose()
