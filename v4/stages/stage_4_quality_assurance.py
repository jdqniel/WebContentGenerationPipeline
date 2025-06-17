import json
import os
from typing import Dict, Any

from openai import AsyncOpenAI

from .base_stage import BaseStage
from ..utils.openai_client import get_openai_async_client


class QualityAssuranceStage(BaseStage):
    """
    Final stage that performs quality assurance on the pipeline input configuration
    and the generated output content.
    """
    def __init__(self, prompts_path: str):
        super().__init__(stage_name="Quality Assurance")
        self.client: AsyncOpenAI = get_openai_async_client()
        self.prompts_path = prompts_path
        self._load_prompt_template()

    def _load_prompt_template(self):
        prompt_file = os.path.join(self.prompts_path, "6_quality_assurance_prompt.txt")
        with open(prompt_file, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"  -> {self.stage_name}: Evaluating input and output quality...")

        job_details = state.get("job_details", {})
        input_config = job_details.get("request_config", {})

        pipeline_output = {
            "content_details": state.get("content_details", {}),
            "seo_package": state.get("seo_package", {}),
            "social_media": state.get("social_media", {}),
            "strategy_context": state.get("strategy_context", {}),
        }

        input_config_str = json.dumps(input_config, indent=2, ensure_ascii=False)
        pipeline_output_str = json.dumps(pipeline_output, indent=2, ensure_ascii=False)

        prompt = self.prompt_template.format(
            input_config=input_config_str,
            pipeline_output=pipeline_output_str
        )
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        qa_report = response.choices[0].message.content
        usage = response.usage

        state["quality_assurance"] = qa_report

        if "usage_statistics" in job_details:
            stats = job_details["usage_statistics"]
            stats["prompt_tokens"] += usage.prompt_tokens
            stats["completion_tokens"] += usage.completion_tokens
            stats["total_tokens"] += usage.prompt_tokens + usage.completion_tokens

        return state