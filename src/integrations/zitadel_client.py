"""Zitadel IAM client for authentication and authorization.

Zitadel provides open-source identity and access management.
This module handles OAuth 2.0, OIDC, and API authentication for PIPE.
"""

import logging
import os
from typing import Dict, Any, Optional, List
import aiohttp
import jwt
from datetime import datetime, timedelta


class ZitadelClient:
    """
    Client for Zitadel identity and access management.

    Provides OAuth 2.0, OIDC, user management, and RBAC integration.
    """

    def __init__(
        self,
        issuer: str = None,
        client_id: str = None,
        client_secret: str = None,
        project_id: str = None,
    ):
        """
        Initialize Zitadel client.

        Args:
            issuer: Zitadel issuer URL
            client_id: OAuth client ID
            client_secret: OAuth client secret
            project_id: Zitadel project ID
        """
        self.issuer = issuer or os.getenv("ZITADEL_ISSUER", "http://localhost:8080")
        self.client_id = client_id or os.getenv("ZITADEL_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("ZITADEL_CLIENT_SECRET")
        self.project_id = project_id or os.getenv("ZITADEL_PROJECT_ID")
        self.logger = logging.getLogger("pipe.integrations.zitadel")

        self._session: Optional[aiohttp.ClientSession] = None
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get access token using client credentials flow.

        Args:
            force_refresh: Force token refresh even if not expired

        Returns:
            Access token or None
        """
        # Return cached token if still valid
        if (
            not force_refresh
            and self._access_token
            and self._token_expires
            and datetime.now() < self._token_expires
        ):
            return self._access_token

        if not self.client_id or not self.client_secret:
            self.logger.error("Client ID and secret not configured")
            return None

        session = await self._ensure_session()
        url = f"{self.issuer}/oauth/v2/token"

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "openid profile email urn:zitadel:iam:org:project:id:zitadel:aud",
        }

        try:
            async with session.post(
                url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self._access_token = data["access_token"]
                    expires_in = data.get("expires_in", 3600)
                    self._token_expires = datetime.now() + timedelta(
                        seconds=expires_in - 60
                    )  # 60s buffer
                    self.logger.info("Successfully obtained access token")
                    return self._access_token
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Failed to get access token: {response.status} - {error_text}"
                    )
                    return None
        except Exception as e:
            self.logger.error(f"Error getting access token: {str(e)}")
            return None

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token claims or None
        """
        session = await self._ensure_session()
        url = f"{self.issuer}/oauth/v2/introspect"

        access_token = await self.get_access_token()
        if not access_token:
            return None

        payload = {"token": token, "client_id": self.client_id}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            async with session.post(url, data=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("active"):
                        return data
                    else:
                        self.logger.warning("Token is not active")
                        return None
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Token verification failed: {response.status} - {error_text}"
                    )
                    return None
        except Exception as e:
            self.logger.error(f"Error verifying token: {str(e)}")
            return None

    async def create_service_account(
        self, name: str, roles: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a service account (machine user).

        Args:
            name: Service account name
            roles: List of role IDs to assign

        Returns:
            Service account details or None
        """
        access_token = await self.get_access_token()
        if not access_token:
            return None

        session = await self._ensure_session()
        url = f"{self.issuer}/management/v1/users/machine"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "userName": name,
            "name": name,
            "description": f"PIPE service account: {name}",
            "accessTokenType": "ACCESS_TOKEN_TYPE_JWT",
        }

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    user_id = data["userId"]
                    self.logger.info(f"Created service account: {name} ({user_id})")

                    # Assign roles if provided
                    if roles:
                        await self._assign_roles(user_id, roles, access_token)

                    return data
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Failed to create service account: {response.status} - {error_text}"
                    )
                    return None
        except Exception as e:
            self.logger.error(f"Error creating service account: {str(e)}")
            return None

    async def _assign_roles(
        self, user_id: str, roles: List[str], access_token: str
    ) -> bool:
        """Assign roles to a user."""
        session = await self._ensure_session()

        for role in roles:
            url = f"{self.issuer}/management/v1/users/{user_id}/grants"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            payload = {"projectId": self.project_id, "roleKeys": [role]}

            try:
                async with session.post(
                    url, json=payload, headers=headers
                ) as response:
                    if response.status in [200, 201]:
                        self.logger.info(f"Assigned role {role} to user {user_id}")
                    else:
                        error_text = await response.text()
                        self.logger.error(
                            f"Failed to assign role: {response.status} - {error_text}"
                        )
                        return False
            except Exception as e:
                self.logger.error(f"Error assigning role: {str(e)}")
                return False

        return True

    async def check_permission(
        self, user_id: str, permission: str, resource: str = None
    ) -> bool:
        """
        Check if user has a specific permission.

        Args:
            user_id: User ID
            permission: Permission to check
            resource: Optional resource identifier

        Returns:
            True if user has permission
        """
        access_token = await self.get_access_token()
        if not access_token:
            return False

        session = await self._ensure_session()
        url = f"{self.issuer}/management/v1/users/{user_id}/grants/_search"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = {"query": {"limit": 100}, "sortingColumn": "GRANT_CREATION_DATE"}

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    grants = data.get("result", [])

                    # Check if any grant contains the permission
                    for grant in grants:
                        if permission in grant.get("roleKeys", []):
                            return True

                    return False
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Permission check failed: {response.status} - {error_text}"
                    )
                    return False
        except Exception as e:
            self.logger.error(f"Error checking permission: {str(e)}")
            return False

    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information.

        Args:
            user_id: User ID

        Returns:
            User information or None
        """
        access_token = await self.get_access_token()
        if not access_token:
            return None

        session = await self._ensure_session()
        url = f"{self.issuer}/management/v1/users/{user_id}"

        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("user", {})
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Failed to get user info: {response.status} - {error_text}"
                    )
                    return None
        except Exception as e:
            self.logger.error(f"Error getting user info: {str(e)}")
            return None

    async def create_project_role(
        self, role_key: str, display_name: str, group: str = None
    ) -> bool:
        """
        Create a project role.

        Args:
            role_key: Role key (e.g., "domain-admin")
            display_name: Human-readable role name
            group: Optional role group

        Returns:
            True if created successfully
        """
        access_token = await self.get_access_token()
        if not access_token:
            return False

        session = await self._ensure_session()
        url = f"{self.issuer}/management/v1/projects/{self.project_id}/roles"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = {"roleKey": role_key, "displayName": display_name}

        if group:
            payload["group"] = group

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status in [200, 201]:
                    self.logger.info(f"Created project role: {role_key}")
                    return True
                elif response.status == 409:
                    self.logger.info(f"Role already exists: {role_key}")
                    return True
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"Failed to create role: {response.status} - {error_text}"
                    )
                    return False
        except Exception as e:
            self.logger.error(f"Error creating role: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """
        Check Zitadel server health.

        Returns:
            True if healthy
        """
        session = await self._ensure_session()
        url = f"{self.issuer}/debug/healthz"

        try:
            async with session.get(url) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False


# Singleton instance
_zitadel_client: Optional[ZitadelClient] = None


async def get_zitadel_client(
    issuer: str = None, client_id: str = None, client_secret: str = None
) -> ZitadelClient:
    """
    Get or create Zitadel client singleton.

    Args:
        issuer: Zitadel issuer URL
        client_id: OAuth client ID
        client_secret: OAuth client secret

    Returns:
        Zitadel client instance
    """
    global _zitadel_client

    if _zitadel_client is None:
        _zitadel_client = ZitadelClient(
            issuer=issuer, client_id=client_id, client_secret=client_secret
        )

    return _zitadel_client
