# web_content_pipeline/stages/stage_2_generation.py
import json
import asyncio
from .base_stage import PipelineStage
from utils.openai_client import client

class GenerationStage(PipelineStage):
    """
    Stage 2: Implements an async multi-step "outline-and-fill" generation process
    by running section-writing tasks concurrently.
    """
    def __init__(self, outline_prompt_path: str, writer_prompt_path: str, seo_prompt_path: str):
        # Load all prompt templates during initialization
        with open(outline_prompt_path, 'r', encoding='utf-8') as f:
            self._outline_prompt_template = f.read()
        with open(writer_prompt_path, 'r', encoding='utf-8') as f:
            self._writer_prompt_template = f.read()
        with open(seo_prompt_path, 'r', encoding='utf-8') as f:
            self._seo_prompt_template = f.read()
        
        # Initialize usage stats tracker
        self.usage_stats = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _update_usage(self, usage):
        """Helper to accumulate token usage across multiple API calls."""
        if usage:
            self.usage_stats["prompt_tokens"] += usage.prompt_tokens
            self.usage_stats["completion_tokens"] += usage.completion_tokens
            self.usage_stats["total_tokens"] += usage.total_tokens

    async def _call_api(self, prompt: str, is_json: bool = False, max_tokens: int = None) -> str | None:
        """A generic async helper to make API calls and handle errors."""
        if not client:
            raise ConnectionError("OpenAI client is not initialized.")
        
        try:
            response_format = {"type": "json_object"} if is_json else {"type": "text"}
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format=response_format,
                max_tokens=max_tokens,
                temperature=0.7
            )
            self._update_usage(response.usage)
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"🚨 An error occurred during an API call: {e}")
            return None

    async def _generate_outline(self, config: dict) -> list:
        """First API call: Generate the content outline."""
        print("--- Generating Outline (API Call 1) ---")
        prompt = self._outline_prompt_template.format(
            documentType=config['documentType'],
            partners=", ".join([p['name'] for p in config['partners']]),
            strategy_focus=config['strategy']['specificFocus'],
            content_goal=config['generationConfig']['contentGoal'],
            target_audience=config['generationConfig']['targetAudience']
        )
        outline_response = await self._call_api(prompt, is_json=True)
        return json.loads(outline_response).get("outline", []) if outline_response else []

    async def _write_section(self, section_title: str, config: dict) -> str:
        """Prepares and executes an API call to write a single content section."""
        print(f"--- Writing section: {section_title} ---")
        prompt = self._writer_prompt_template.format(
            content_tone=config['generationConfig']['contentTone'],
            partners=", ".join([p['name'] for p in config['partners']]),
            content_goal=config['generationConfig']['contentGoal'],
            section_title=section_title
        )
        return await self._call_api(prompt, max_tokens=500)

    async def _generate_seo(self, title: str, body: str) -> dict:
        """Final API call: Generate SEO assets based on the full content."""
        print("--- Generating SEO Assets (Final API Call) ---")
        prompt = self._seo_prompt_template.format(title=title, body=body)
        seo_response = await self._call_api(prompt, is_json=True)
        return json.loads(seo_response) if seo_response else {}

    async def execute(self, context: dict) -> dict:
        print("--- Executing Stage 2: Async Multi-Step Content Generation ---")
        config = context['config']
        
        # 1. Generate the outline (first synchronous step in this stage)
        outline = await self._generate_outline(config)
        if not outline:
            print("🚨 Failed to generate outline. Stopping generation.")
            context['generated_content'] = {"error": "Could not generate content outline."}
            context['seo_assets'] = {}
            context['usage_stats'] = self.usage_stats
            return context
        
        # 2. Create a list of async tasks for writing all sections
        writing_tasks = [self._write_section(title, config) for title in outline]
        
        # 3. Execute all writing tasks concurrently
        print(f"--- Writing {len(writing_tasks)} sections in parallel (Concurrent API Calls) ---")
        section_contents = await asyncio.gather(*writing_tasks)
        
        # 4. Assemble the results
        body_blocks = []
        body_markdown_parts = []
        for i, section_title in enumerate(outline):
            content = section_contents[i]
            if content:
                body_blocks.append({"type": "heading", "level": 2, "text": section_title})
                body_blocks.append({"type": "paragraph", "text": content})
                body_markdown_parts.append(f"## {section_title}\n\n{content}")

        # 5. Assemble final content and generate SEO assets
        title = outline[0] if outline else "Generated Title"
        full_body_markdown = "\n\n".join(body_markdown_parts)
        
        seo_assets = await self._generate_seo(title, full_body_markdown)
        
        context['generated_content'] = {
            "title": seo_assets.get("meta_title", title),
            "body_blocks": body_blocks,
            "body_markdown": full_body_markdown
        }
        context['seo_assets'] = seo_assets
        context['usage_stats'] = self.usage_stats
        print("✅ All sections and assets generated successfully.")
        return context