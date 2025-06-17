from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, Any

from .base_stage import BaseStage

class AssemblyStage(BaseStage):
    """
    Final stage that assembles all the generated pieces into a final JSON document.
    """
    def __init__(self):
        super().__init__(stage_name="Assembly")

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the data from the state and builds the final output object.
        """
        print(f"  -> {self.stage_name}: Assembling the final document...")

        # Extract all the pieces from the state
        request_config = state.get('request_config', {})
        usage_stats = state.get('usage_statistics', {})
        outline = state.get('generated_outline', {})
        sections_content = state.get('generated_sections', [])
        seo_assets = state.get('generated_seo', {})

        # Build raw text of the content with optional CTA
        raw_sections = "\n\n".join(section.get('content', '') for section in sections_content)
        cta_text = state.get('generated_cta', {}).get('cta_text', '')
        full_content = f"{raw_sections}\n\n{cta_text}".strip()
        summary = state.get('generated_summary', {}).get('description', '')
        content_details = {
            "title": outline.get('title', 'Untitled Document'),
            "description": summary,
            "content_length_in_words": len(full_content.split()),
            "full_content": full_content
        }
        seo_package = {
            "meta_description": seo_assets.get('meta_description'),
            "keywords": seo_assets.get('suggested_keywords')
        }
        social = state.get('generated_social_media_post', {})
        social_media = {
            "social_title": outline.get('title', 'Untitled Document'),
            "social_description": social.get('postContent')
        }
        strategy = request_config.get('strategy', {})
        partners_list = [p.get('name') for p in request_config.get('partners', [])]
        strategy_context = {
            "category": strategy.get('category'),
            "focus": strategy.get('specificFocus'),
            "partners": partners_list
        }
        # Add job details for observability
        job_details = {
            "generation_id": str(uuid4()),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "usage_statistics": state.get('usage_statistics', {}),
            "request_config": request_config
        }
        final_result = {
            "job_details": job_details,
            "content_details": content_details,
            "seo_package": seo_package,
            "social_media": social_media,
            "strategy_context": strategy_context
        }
        
        # This stage replaces the state with the final result
        return final_result