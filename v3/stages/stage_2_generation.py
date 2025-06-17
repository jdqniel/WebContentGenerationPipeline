import asyncio
import json
import os
from typing import Dict, Any, List, Tuple

from openai import AsyncOpenAI

from .base_stage import BaseStage
from ..utils.openai_client import get_openai_async_client


class GenerationStage(BaseStage):
    """
    Content generation stage.

    Orchestrates multiple calls to the OpenAI API to generate the outline,
    the section content (in parallel), and the SEO assets.
    """

    def __init__(self, prompts_path: str):
        super().__init__(stage_name="Content Generation")
        self.client: AsyncOpenAI = get_openai_async_client()
        self.prompts_path = prompts_path
        self._load_prompt_templates()

    def _load_prompt_templates(self):
        """Loads the static prompts (section writer, SEO, social media, summary)."""
        with open(os.path.join(self.prompts_path, '2_section_writer_prompt.txt'), 'r', encoding='utf-8') as f:
            self.section_writer_prompt_template = f.read()
        with open(os.path.join(self.prompts_path, '3_seo_assets_prompt.txt'), 'r', encoding='utf-8') as f:
            self.seo_assets_prompt_template = f.read()
        with open(os.path.join(self.prompts_path, '4_social_media_prompt.txt'), 'r', encoding='utf-8') as f:
            self.social_media_prompt_template = f.read()
        with open(os.path.join(self.prompts_path, '5_summary_prompt.txt'), 'r', encoding='utf-8') as f:
            self.summary_prompt_template = f.read()
        with open(os.path.join(self.prompts_path, '6_cta_prompt.txt'), 'r', encoding='utf-8') as f:
            self.cta_prompt_template = f.read()

    def _load_outline_prompt(self, document_type: str):
        """Loads the outline prompt template, preferring a type-specific file if available."""
        slug = document_type.lower().replace(' ', '_')
        type_path = os.path.join(self.prompts_path, f'outline_{slug}_prompt.txt')
        if os.path.exists(type_path):
            with open(type_path, 'r', encoding='utf-8') as f:
                self.outline_prompt_template = f.read()
        else:
            with open(os.path.join(self.prompts_path, '1_outline_prompt.txt'), 'r', encoding='utf-8') as f:
                self.outline_prompt_template = f.read()

    async def _generate_outline(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], int, int]:
        """Generates the document outline."""
        print("    -> Sub-stage: generating outline...")
        prompt = self.outline_prompt_template.format(
            documentType=config.get('documentType', 'article'),
            partners=", ".join([p['name'] for p in config.get('partners', [])]),
            strategy_focus=config.get('strategy', {}).get('specificFocus', ''),
            content_goal=config.get('generationConfig', {}).get('contentGoal', ''),
            target_audience=config.get('generationConfig', {}).get('targetAudience', '')
        )
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        outline_json = json.loads(response.choices[0].message.content)
        usage = response.usage
        return outline_json, usage.prompt_tokens, usage.completion_tokens

    async def _generate_single_section(self, section_title: str, config: Dict[str, Any]) -> Tuple[str, int, int]:
        """Generates the content for a single section."""
        prompt = self.section_writer_prompt_template.format(
            section_title=section_title,
            content_tone=config.get('generationConfig', {}).get('contentTone', 'neutral'),
            partners=", ".join([p['name'] for p in config.get('partners', [])]),
            content_goal=config.get('generationConfig', {}).get('contentGoal', ''),
            strategy_focus=config.get('strategy', {}).get('specificFocus', 'our amazing partners')
        )
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        usage = response.usage
        return content, usage.prompt_tokens, usage.completion_tokens

    async def _generate_all_sections(self, outline: Dict[str, Any], config: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int, int]:
        """Generates the content for all sections in parallel."""
        section_titles = outline.get('body', [])
        print(f"    -> Sub-stage: generating {len(section_titles)} sections in parallel...")
        
        tasks = [self._generate_single_section(title, config) for title in section_titles]
        results = await asyncio.gather(*tasks)
        
        total_prompt_tokens = sum(r[1] for r in results)
        total_completion_tokens = sum(r[2] for r in results)
        
        generated_sections = []
        for i, title in enumerate(section_titles):
            content, _, _ = results[i]
            generated_sections.append({
                "title": title,
                "content": content
            })
            
        return generated_sections, total_prompt_tokens, total_completion_tokens
        
    async def _generate_seo_assets(self, title: str, full_content: str) -> Tuple[Dict[str, Any], int, int]:
        """Generates the SEO assets."""
        print("    -> Sub-stage: generating SEO assets...")
        prompt = self.seo_assets_prompt_template.format(
            title=title,
            body=full_content
        )
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        seo_json = json.loads(response.choices[0].message.content)
        usage = response.usage
        return seo_json, usage.prompt_tokens, usage.completion_tokens

    async def _generate_social_media_post(self, title: str, full_content: str) -> Tuple[Dict[str, Any], int, int]:
        """Generates a social media post JSON promoting the article."""
        print("    -> Sub-stage: generating social media post...")
        prompt = self.social_media_prompt_template.format(
            title=title,
            body=full_content
        )
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        post_json = json.loads(response.choices[0].message.content)
        usage = response.usage
        return post_json, usage.prompt_tokens, usage.completion_tokens

    async def _generate_summary(self, title: str, full_content: str) -> Tuple[Dict[str, Any], int, int]:
        """Generates a concise summary description of the article."""
        print("    -> Sub-stage: generating summary description...")
        prompt = self.summary_prompt_template.format(
            title=title,
            body=full_content
        )
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        summary_json = json.loads(response.choices[0].message.content)
        usage = response.usage
        return summary_json, usage.prompt_tokens, usage.completion_tokens

    async def _generate_cta(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], int, int]:
        """Generates a compelling call-to-action."""
        print("    -> Sub-stage: generating call-to-action...")
        prompt = self.cta_prompt_template.format(
            content_goal=config.get('generationConfig', {}).get('contentGoal', ''),
            target_audience=config.get('generationConfig', {}).get('targetAudience', ''),
            partners=", ".join([p['name'] for p in config.get('partners', [])])
        )
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        cta_json = json.loads(response.choices[0].message.content)
        usage = response.usage
        return cta_json, usage.prompt_tokens, usage.completion_tokens

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the full logic of the generation stage."""
        config = state['request_config']
        
        # Load static prompt templates, then type-specific outline prompt
        self._load_prompt_templates()
        self._load_outline_prompt(config.get('documentType', ''))
        outline_json, pt_1, ct_1 = await self._generate_outline(config)
        
        # 2. Generate sections in parallel
        generated_sections, pt_2, ct_2 = await self._generate_all_sections(outline_json, config)
        
        # 3. Generate SEO
        full_content_for_seo = "\n\n".join([f"## {s['title']}\n{s['content']}" for s in generated_sections])
        seo_json, pt_3, ct_3 = await self._generate_seo_assets(
            outline_json.get('title', 'Untitled Document'), full_content_for_seo
        )

        # 4b. Generate social media post
        social_post_json, pt_4, ct_4 = await self._generate_social_media_post(
            outline_json.get('title', 'Untitled Document'), full_content_for_seo
        )

        # 4c. Generate summary description
        summary_json, pt_5, ct_5 = await self._generate_summary(
            outline_json.get('title', 'Untitled Document'), full_content_for_seo
        )

        # 5. Generate CTA if required
        requires_cta = state.get('derived_instructions', {}).get('requires_cta', False)
        if requires_cta:
            cta_json, pt_6, ct_6 = await self._generate_cta(config)
            state['generated_cta'] = cta_json
        else:
            pt_6, ct_6 = 0, 0
            state['generated_cta'] = {}

        # 6. Consolidate results into the state
        state['generated_outline'] = outline_json
        state['generated_sections'] = generated_sections
        state['generated_seo'] = seo_json
        state['generated_social_media_post'] = social_post_json
        state['generated_summary'] = summary_json
        state['usage_statistics'] = {
            "prompt_tokens": pt_1 + pt_2 + pt_3 + pt_4 + pt_5 + pt_6,
            "completion_tokens": ct_1 + ct_2 + ct_3 + ct_4 + ct_5 + ct_6,
            "total_tokens": (
                pt_1 + ct_1 + pt_2 + ct_2 + pt_3 + ct_3 + pt_4 + ct_4 + pt_5 + ct_5 + pt_6 + ct_6
            ),
        }

        return state