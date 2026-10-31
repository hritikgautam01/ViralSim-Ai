"""
ViralSim AI - Base Agent Foundation
Provides structured LLM interaction, JSON schema parsing, retries, and fallback safety.
"""

import json
import logging
import time
from typing import Any, Dict, Optional
from backend.agents.config import get_llm_client, is_llm_available, LLM_MODEL_NAME

logger = logging.getLogger("viralsim.agents")

class BaseAgent:
    """Base class for all specialized AI agents in the ViralSim simulation system."""
    
    agent_id: str = "base_agent"
    agent_name: str = "Base Agent"
    agent_title: str = "General Analyst"
    agent_emoji: str = "🤖"
    agent_color: str = "#A8B99B"
    system_prompt: str = "You are a professional video analytics AI agent. Always reply with valid JSON."
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or LLM_MODEL_NAME

    def call_llm_json(self, user_prompt: str, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes an LLM request expecting a JSON object response.
        If LLM is unavailable or fails, returns fallback_data with graceful degradation.
        """
        start_time = time.time()
        
        if not is_llm_available():
            logger.warning(f"[{self.agent_name}] LLM key not configured. Using intelligent fallback heuristics.")
            fallback = fallback_data or {}
            fallback["_agent_meta"] = self.get_metadata(start_time, is_fallback=True)
            return fallback

        try:
            client = get_llm_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            raw_text = response.choices[0].message.content or "{}"
            parsed = json.loads(raw_text)
            parsed["_agent_meta"] = self.get_metadata(start_time, is_fallback=False)
            return parsed
        except Exception as e:
            logger.error(f"[{self.agent_name}] LLM invocation error: {e}. Falling back to default heuristics.")
            fallback = fallback_data or {}
            fallback["_agent_meta"] = self.get_metadata(start_time, is_fallback=True, error=str(e))
            return fallback

    def get_metadata(self, start_time: float, is_fallback: bool = False, error: Optional[str] = None) -> Dict[str, Any]:
        """Returns standard metadata for agent transparency and audit trail."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_title": self.agent_title,
            "agent_emoji": self.agent_emoji,
            "agent_color": self.agent_color,
            "model": self.model if not is_fallback else "heuristic-fallback",
            "is_ai_generated": not is_fallback,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "error": error
        }

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Subclasses must implement this method."""
        raise NotImplementedError("Each agent must implement analyze(context).")

