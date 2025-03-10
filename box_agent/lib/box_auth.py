from typing import Optional
from box_sdk_gen import (
    BoxClient,
    CCGConfig,
    BoxCCGAuth,
    FileWithInMemoryCacheTokenStorage,
    OAuthConfig,
    BoxOAuth,
    GetAuthorizeUrlOptions,
    AccessToken,
)
from dotenv import load_dotenv
import os
import uuid

class BoxAuth:

    def __init__(self):
        load_dotenv()
        # Environment variables
        self.CLIENT_ID = os.getenv("BOX_CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("BOX_CLIENT_SECRET")
        # CCG
        self.SUBJECT_TYPE = os.getenv("BOX_SUBJECT_TYPE")
        self.SUBJECT_ID = os.getenv("BOX_SUBJECT_ID")

        self.client = self.get_ccg_client()


    def get_ccg_config(self) -> CCGConfig:
        if self.SUBJECT_TYPE == "enterprise":
            enterprise_id = self.SUBJECT_ID
            user_id = None
        else:
            enterprise_id = None
            user_id = self.SUBJECT_ID

        return CCGConfig(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            enterprise_id=enterprise_id,
            user_id=user_id,
            token_storage=FileWithInMemoryCacheTokenStorage(".auth.ccg"),
        )


    def get_ccg_client(self) -> BoxClient:
        conf = self.get_ccg_config()
        auth = BoxCCGAuth(conf)
        return self.add_extra_header_to_box_client(BoxClient(auth))



    def add_extra_header_to_box_client(self, box_client: BoxClient) -> BoxClient:
        """
        Add extra headers to the Box client.

        Args:
            box_client (BoxClient): A Box client object.
            header (Dict[str, str]): A dictionary of extra headers to add to the Box client.

        Returns:
            BoxClient: A Box client object with the extra headers added.
        """
        header = {"x-box-ai-library": "oai-response-api"}
        return box_client.with_extra_headers(extra_headers=header)


    def get_client(self) -> BoxClient:
        
        if self.client is None:
            self.client = self.get_ccg_client()
            
        return self.client
