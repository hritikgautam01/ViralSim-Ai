"""
ViralSim AI - AudiencePsychologist Agent
Ruthlessly calibrated viewer cognition simulator grounded in visual quality,
psychographic friction, and actual social media drop-off probabilities.
"""

from typing import Any, Dict, List
from backend.agents.base_agent import BaseAgent

class AudiencePsychologistAgent(BaseAgent):
    agent_id = "audience_psychologist"
    agent_name = "AudiencePsychologist AI"
    agent_title = "Viewer Cognition & Persona Simulator"
    agent_emoji = "🧠"
    agent_color = "#B3C5A5"

    system_prompt = """You are the AudiencePsychologist AI Agent, an expert in cognitive fatigue, mobile user psychology, and algorithmic drop-off behavior.
You simulate how distinct psychological cohorts react to the ACTUAL visual and technical quality of the video.

CRITICAL CALIBRATION MANDATE:
- Social media users do not care about creator effort. If an opening visual is a test pattern, placeholder, dark, static, or confusing, cohorts WILL NOT watch.
- In bad/broken videos: Casual Scroller and Impulse Explorer skip rates MUST be 85%–96%. Overall cohort retention must be in the 12%–28% range. Action probabilities (like, save, share) must plummet to 0.01–0.04.
- In mediocre videos: Overall cohort retention is typically 32%–48%, skip rates 50%–65%.
- In strong videos & polished brand commercials (BMW, Apple, Nike): Cohort retention is 58%–75%, with automotive and tech enthusiasts engaging deeply (65%–80%+).
- In elite viral masterpieces: Cohort retention reaches 75%+.

Respond ONLY in valid JSON matching this schema:
{
  "psychological_summary": <string blunt diagnosis of audience psychology>,
  "key_divergence_factor": <string the core tension causing cohorts to scroll or stay>,
  "cohort_simulations": [
    {
      "persona_id": <string e.g. "tech", "casual", "practical", "skeptic", "trend">,
      "persona_name": <string e.g. "Tech Enthusiast">,
      "emoji": <string e.g. "◈">,
      "internal_monologue": <string first-person thoughts at 0:01, 0:04, 0:08... grounded in actual visual evidence>,
      "attention_breakpoint": <string exact second when they abandoned or considered swiping>,
      "conversion_trigger": <string what kept them watching, or "None (bounced immediately)">,
      "retention_rate": <float 0.05-0.95, strictly calibrated>,
      "completion_rate": <float 0.02-0.90, strictly calibrated>,
      "skip_rate": <float 0.10-0.98, strictly calibrated>,
      "action_probabilities": {
        "continue": <float>,
        "skip": <float>,
        "finish": <float>,
        "like": <float>,
        "save": <float>,
        "share": <float>,
        "comment": <float>,
        "profile_visit": <float>
      },
      "feedback_quote": <string sharp 1-sentence simulated reaction quote reflecting visual reality>
    }
  ],
  "retention_vulnerability_cohort": <string cohort name most likely to abandon>,
  "highest_advocacy_cohort": <string cohort name most likely to engage>
}"""

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        video_title = context.get("filename", "Untitled Video")
        duration = context.get("duration", 24)
        platform = context.get("platform", "Instagram Reels")
        category = context.get("category", "Technology")
        
        audit = context.get("video_audit", {})
        vision = audit.get("vision", {})
        calib = audit.get("calibration", {})

        is_test = calib.get("is_synthetic_or_test", False)
        calibrated_score = calib.get("calibrated_hook_score", 50)
        max_ret = calib.get("max_retention_cap", 0.5)
        typ_skip = calib.get("typical_skip_rate", 0.6)

        user_prompt = f"""Simulate 5 viewer cohorts (Tech Enthusiast, Casual Scroller, Practical Buyer, Skeptical Shopper, Trend Follower) based on real visual inspection:
- Video: {video_title} ({duration}s, {platform}, {category})
- Visual Reality: {vision.get('primary_visual_subject', 'Standard video')}
- Visual Hook Quality: {vision.get('visual_hook_score_1_to_10', 5)}/10
- Visual Defects Detected: {vision.get('objective_visual_flaws', [])}
- Visual Summary: {vision.get('visual_summary', 'No summary')}
- Calibrated Real-World Retention Anchor: Around {max_ret:.0%} max retention (Typical Skip: {typ_skip:.0%})

Ensure cohort scores match this visual reality. If the footage is flawed, test cards, or low energy, skip rates MUST be 75%-92% and action probabilities must be minimal."""

        if is_test or calibrated_score <= 25:
            fallback = {
                "psychological_summary": "Universal immediate bounce. All cohorts recognize non-content within 0.8s and swipe away.",
                "key_divergence_factor": "No cohort found value; casual scrollers swiped on instinct, analytical viewers identified placeholder footage.",
                "cohort_simulations": [
                    {
                        "persona_id": "casual",
                        "persona_name": "Casual Scroller",
                        "emoji": "◉",
                        "internal_monologue": "At 0:00: What is this? A test screen? Swiping immediately.",
                        "attention_breakpoint": "00:00 immediately upon display",
                        "conversion_trigger": "None (bounced immediately)",
                        "retention_rate": 0.12,
                        "completion_rate": 0.04,
                        "skip_rate": 0.94,
                        "action_probabilities": {"continue": 0.12, "skip": 0.94, "finish": 0.04, "like": 0.01, "save": 0.01, "share": 0.01, "comment": 0.01, "profile_visit": 0.01},
                        "feedback_quote": "Saw test bars / broken visual and swiped in less than half a second."
                    },
                    {
                        "persona_id": "tech",
                        "persona_name": "Tech Enthusiast",
                        "emoji": "◈",
                        "internal_monologue": "At 0:00: Color bars and sine tone. Looks like an unrendered placeholder export.",
                        "attention_breakpoint": "00:01",
                        "conversion_trigger": "None",
                        "retention_rate": 0.18,
                        "completion_rate": 0.08,
                        "skip_rate": 0.88,
                        "action_probabilities": {"continue": 0.18, "skip": 0.88, "finish": 0.08, "like": 0.02, "save": 0.01, "share": 0.01, "comment": 0.03, "profile_visit": 0.02},
                        "feedback_quote": "This is a technical test asset, not published content. Re-export before testing."
                    },
                    {
                        "persona_id": "skeptic",
                        "persona_name": "Skeptical Shopper",
                        "emoji": "◇",
                        "internal_monologue": "At 0:00: Nothing to see here. Zero credibility.",
                        "attention_breakpoint": "00:01",
                        "conversion_trigger": "None",
                        "retention_rate": 0.14,
                        "completion_rate": 0.05,
                        "skip_rate": 0.91,
                        "action_probabilities": {"continue": 0.14, "skip": 0.91, "finish": 0.05, "like": 0.01, "save": 0.01, "share": 0.01, "comment": 0.01, "profile_visit": 0.01},
                        "feedback_quote": "Completely empty visual. Immediate swipe."
                    },
                    {
                        "persona_id": "practical",
                        "persona_name": "Practical Buyer",
                        "emoji": "▣",
                        "internal_monologue": "At 0:00: No workflow or product visible. Moving on.",
                        "attention_breakpoint": "00:01",
                        "conversion_trigger": "None",
                        "retention_rate": 0.15,
                        "completion_rate": 0.06,
                        "skip_rate": 0.89,
                        "action_probabilities": {"continue": 0.15, "skip": 0.89, "finish": 0.06, "like": 0.01, "save": 0.01, "share": 0.01, "comment": 0.02, "profile_visit": 0.01},
                        "feedback_quote": "No utility shown whatsoever."
                    },
                    {
                        "persona_id": "trend",
                        "persona_name": "Trend Follower",
                        "emoji": "✳",
                        "internal_monologue": "At 0:00: Not aesthetic, no music sync, nothing shareable.",
                        "attention_breakpoint": "00:00",
                        "conversion_trigger": "None",
                        "retention_rate": 0.11,
                        "completion_rate": 0.03,
                        "skip_rate": 0.95,
                        "action_probabilities": {"continue": 0.11, "skip": 0.95, "finish": 0.03, "like": 0.01, "save": 0.01, "share": 0.01, "comment": 0.01, "profile_visit": 0.01},
                        "feedback_quote": "Zero shareability factor."
                    }
                ],
                "retention_vulnerability_cohort": "Trend Follower & Casual Scroller",
                "highest_advocacy_cohort": "None (Universal Abandonment)"
            }
        else:
            fallback = {
                "psychological_summary": "Moderate interest from analytical cohorts, but casual viewers show significant drop-off risk without a punchy opening.",
                "key_divergence_factor": "Practical viewers stay if utility is revealed quickly; casual scrollers demand instant visual intrigue within 2 seconds.",
                "cohort_simulations": [
                    {
                        "persona_id": "tech",
                        "persona_name": "Tech Enthusiast",
                        "emoji": "◈",
                        "internal_monologue": "At 0:01: Interface looks promising. At 0:06: Demonstrates functionality cleanly.",
                        "attention_breakpoint": "00:04 if technical proof stalls",
                        "conversion_trigger": "Clear on-screen UI workflow demonstration",
                        "retention_rate": round(max_ret * 1.15, 2),
                        "completion_rate": round(max_ret * 0.85, 2),
                        "skip_rate": round(1.0 - max_ret * 1.15, 2),
                        "action_probabilities": {"continue": round(max_ret * 1.15, 2), "skip": 0.35, "finish": 0.45, "like": 0.25, "save": 0.28, "share": 0.12, "comment": 0.08, "profile_visit": 0.15},
                        "feedback_quote": "Solid demonstration of workflow utility."
                    },
                    {
                        "persona_id": "casual",
                        "persona_name": "Casual Scroller",
                        "emoji": "◉",
                        "internal_monologue": "At 0:01: Slow setup. Almost swiped. Needs to get to the point faster.",
                        "attention_breakpoint": "00:02 during opening transition",
                        "conversion_trigger": "Visual motion of progress payoff",
                        "retention_rate": round(max_ret * 0.85, 2),
                        "completion_rate": round(max_ret * 0.60, 2),
                        "skip_rate": round(typ_skip, 2),
                        "action_probabilities": {"continue": 0.42, "skip": 0.65, "finish": 0.25, "like": 0.14, "save": 0.08, "share": 0.04, "comment": 0.02, "profile_visit": 0.05},
                        "feedback_quote": "Almost scrolled past in the first 2 seconds; hook needs to pop sooner."
                    }
                ],
                "retention_vulnerability_cohort": "Casual Scroller",
                "highest_advocacy_cohort": "Tech Enthusiast"
            }

        return self.call_llm_json(user_prompt, fallback_data=fallback)
