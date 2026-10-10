import os
import boto3
from botocore.config import Config
from typing import Any, Dict, Optional

class BedrockLLM:
    def __init__(
        self,
        model_id: Optional[str] = None,
        region_name: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 700,
        client: Optional[Any] = None,
    ):
        self.model_id = model_id or os.environ.get("BEDROCK_MODEL_ID")
        if not self.model_id:
            raise ValueError("BEDROCK_MODEL_ID environment variable is required")
        self.region_name = region_name or os.environ.get("AWS_REGION", "ap-south-1")
        self.temperature = temperature
        self.max_tokens = max_tokens

        if client is not None:
            self.client = client
        else:
            boto_config = Config(
                read_timeout=20,
                retries={"max_attempts": 3, "mode": "standard"},
            )
            self.client = boto3.client(
                "bedrock-runtime",
                region_name=self.region_name,
                config=boto_config,
            )

    def invoke(self, prompt: str) -> str:
        response = self.client.converse(
            modelId=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            inferenceConfig={
                "temperature": self.temperature,
                "maxTokens": self.max_tokens,
            },
        )
        output_content = response.get("output", {}).get("message", {}).get("content", [])
        if output_content and "text" in output_content[0]:
            return output_content[0]["text"]
        return ""
