"""OpenBao client for secrets management.

OpenBao is the open-source fork of HashiCorp Vault (forbidden).
This module provides secrets management integration for PIPE bots.
"""

import logging
import os
from typing import Dict, Any, Optional
import aiohttp
import json
from pathlib import Path


class OpenBaoClient:
    """
    Client for OpenBao secrets management.

    Replaces HashiCorp Vault with open-source OpenBao fork.
    Provides dynamic secrets, encryption as a service, and PKI.
    """

    def __init__(
        self,
        address: str = None,
        token: str = None,
        namespace: str = None,
        kubernetes_role: str = None,
    ):
        """
        Initialize OpenBao client.

        Args:
            address: OpenBao server address (default: from env OPENBAO_ADDR)
            token: Authentication token (default: from env OPENBAO_TOKEN)
            namespace: OpenBao namespace (default: from env OPENBAO_NAMESPACE)
            kubernetes_role: Kubernetes service account role for auth
        """
        self.address = address or os.getenv("OPENBAO_ADDR", "http://localhost:8200")
        self.token = token or os.getenv("OPENBAO_TOKEN")
        self.namespace = namespace or os.getenv("OPENBAO_NAMESPACE", "")
        self.kubernetes_role = kubernetes_role
        self.logger = logging.getLogger("pipe.integrations.openbao")

        self._session: Optional[aiohttp.ClientSession] = None
        self._authenticated = False

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def authenticate_kubernetes(self, jwt_path: str = None) -> bool:
        """
        Authenticate to OpenBao using Kubernetes service account.

        Args:
            jwt_path: Path to service account JWT token

        Returns:
            True if authentication successful
        """
        if not self.kubernetes_role:
            self.logger.error("Kubernetes role not configured")
            return False

        # Read service account JWT
        jwt_path = jwt_path or "/var/run/secrets/kubernetes.io/serviceaccount/token"
        try:
            with open(jwt_path, "r") as f:
                jwt = f.read().strip()
        except Exception as e:
            self.logger.error(f"Failed to read service account token: {str(e)}")
            return False

        # Authenticate with OpenBao
        session = await self._ensure_session()
        url = f"{self.address}/v1/auth/kubernetes/login"

        headers = {}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace

        payload = {"role": self.kubernetes_role, "jwt": jwt}

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data["auth"]["client_token"]
                    self._authenticated = True
                    self.logger.info("Successfully authenticated to OpenBao")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"OpenBao authentication failed: {response.status} - {error_text}"
                    )
                    return False
        except Exception as e:
            self.logger.error(f"OpenBao authentication error: {str(e)}")
            return False

    async def read_secret(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Read a secret from OpenBao.

        Args:
            path: Secret path (e.g., "secret/data/myapp/config")

        Returns:
            Secret data dictionary or None if not found
        """
        if not self.token:
            self.logger.error("Not authenticated to OpenBao")
            return None

        session = await self._ensure_session()
        url = f"{self.address}/v1/{path}"

        headers = {"X-Vault-Token": self.token}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace

        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # KV v2 returns data nested under 'data.data'
                    if "data" in data and "data" in data["data"]:
                        return data["data"]["data"]
                    return data.get("data", {})
                elif response.status == 404:
                    self.logger.warning(f"Secret not found: {path}")
                    return None
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Failed to read secret: {response.status} - {error_text}"
                    )
                    return None
        except Exception as e:
            self.logger.error(f"Error reading secret: {str(e)}")
            return None

    async def write_secret(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Write a secret to OpenBao.

        Args:
            path: Secret path (e.g., "secret/data/myapp/config")
            data: Secret data dictionary

        Returns:
            True if write successful
        """
        if not self.token:
            self.logger.error("Not authenticated to OpenBao")
            return False

        session = await self._ensure_session()
        url = f"{self.address}/v1/{path}"

        headers = {"X-Vault-Token": self.token}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace

        # KV v2 requires data wrapped in 'data' key
        if "/data/" in path:
            payload = {"data": data}
        else:
            payload = data

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status in [200, 204]:
                    self.logger.info(f"Successfully wrote secret: {path}")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Failed to write secret: {response.status} - {error_text}"
                    )
                    return False
        except Exception as e:
            self.logger.error(f"Error writing secret: {str(e)}")
            return False

    async def delete_secret(self, path: str) -> bool:
        """
        Delete a secret from OpenBao.

        Args:
            path: Secret path

        Returns:
            True if delete successful
        """
        if not self.token:
            self.logger.error("Not authenticated to OpenBao")
            return False

        session = await self._ensure_session()
        url = f"{self.address}/v1/{path}"

        headers = {"X-Vault-Token": self.token}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace

        try:
            async with session.delete(url, headers=headers) as response:
                if response.status in [200, 204]:
                    self.logger.info(f"Successfully deleted secret: {path}")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Failed to delete secret: {response.status} - {error_text}"
                    )
                    return False
        except Exception as e:
            self.logger.error(f"Error deleting secret: {str(e)}")
            return False

    async def encrypt(self, plaintext: str, key_name: str = "pipe") -> Optional[str]:
        """
        Encrypt data using OpenBao transit engine.

        Args:
            plaintext: Data to encrypt
            key_name: Encryption key name

        Returns:
            Encrypted ciphertext or None
        """
        if not self.token:
            self.logger.error("Not authenticated to OpenBao")
            return None

        session = await self._ensure_session()
        url = f"{self.address}/v1/transit/encrypt/{key_name}"

        headers = {"X-Vault-Token": self.token}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace

        # Base64 encode plaintext
        import base64

        plaintext_b64 = base64.b64encode(plaintext.encode()).decode()

        payload = {"plaintext": plaintext_b64}

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["data"]["ciphertext"]
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Encryption failed: {response.status} - {error_text}"
                    )
                    return None
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}")
            return None

    async def decrypt(self, ciphertext: str, key_name: str = "pipe") -> Optional[str]:
        """
        Decrypt data using OpenBao transit engine.

        Args:
            ciphertext: Data to decrypt
            key_name: Encryption key name

        Returns:
            Decrypted plaintext or None
        """
        if not self.token:
            self.logger.error("Not authenticated to OpenBao")
            return None

        session = await self._ensure_session()
        url = f"{self.address}/v1/transit/decrypt/{key_name}"

        headers = {"X-Vault-Token": self.token}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace

        payload = {"ciphertext": ciphertext}

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Base64 decode plaintext
                    import base64

                    plaintext_b64 = data["data"]["plaintext"]
                    return base64.b64decode(plaintext_b64).decode()
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Decryption failed: {response.status} - {error_text}"
                    )
                    return None
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            return None

    async def generate_certificate(
        self, common_name: str, ttl: str = "24h", alt_names: list = None
    ) -> Optional[Dict[str, str]]:
        """
        Generate a TLS certificate using OpenBao PKI.

        Args:
            common_name: Certificate common name
            ttl: Time to live (e.g., "24h", "30d")
            alt_names: Alternative DNS names

        Returns:
            Dictionary with certificate, private_key, ca_chain
        """
        if not self.token:
            self.logger.error("Not authenticated to OpenBao")
            return None

        session = await self._ensure_session()
        url = f"{self.address}/v1/pki/issue/pipe"

        headers = {"X-Vault-Token": self.token}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace

        payload = {"common_name": common_name, "ttl": ttl}

        if alt_names:
            payload["alt_names"] = ",".join(alt_names)

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "certificate": data["data"]["certificate"],
                        "private_key": data["data"]["private_key"],
                        "ca_chain": data["data"].get("ca_chain", []),
                        "serial_number": data["data"]["serial_number"],
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Certificate generation failed: {response.status} - {error_text}"
                    )
                    return None
        except Exception as e:
            self.logger.error(f"Certificate generation error: {str(e)}")
            return None

    async def health_check(self) -> bool:
        """
        Check OpenBao server health.

        Returns:
            True if healthy
        """
        session = await self._ensure_session()
        url = f"{self.address}/v1/sys/health"

        try:
            async with session.get(url) as response:
                # OpenBao returns 200 if initialized and unsealed
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False


# Singleton instance
_openbao_client: Optional[OpenBaoClient] = None


async def get_openbao_client(
    address: str = None, kubernetes_role: str = None
) -> OpenBaoClient:
    """
    Get or create OpenBao client singleton.

    Args:
        address: OpenBao server address
        kubernetes_role: Kubernetes role for authentication

    Returns:
        OpenBao client instance
    """
    global _openbao_client

    if _openbao_client is None:
        _openbao_client = OpenBaoClient(
            address=address, kubernetes_role=kubernetes_role
        )

        # Auto-authenticate if running in Kubernetes
        if kubernetes_role:
            await _openbao_client.authenticate_kubernetes()

    return _openbao_client
