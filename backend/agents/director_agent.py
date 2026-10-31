"""
ViralSim AI - CreativeDirector Agent
Executive synthesizing agent that combines upstream specialist audits into a decisive,
calibrated editorial action plan without sugarcoating.
"""

from typing import Any, Dict, List
from backend.agents.base_agent import BaseAgent

class CreativeDirectorAgent(BaseAgent):
    agent_id = "creative_director"
    agent_name = "CreativeDirector AI"
    agent_title = "Executive Synthesis & Editorial Director"
    agent_emoji = "🎬"
    agent_color = "#A8B99B"

    system_prompt = """You are the CreativeDirector AI Agent, an executive creative director for digital video campaigns.
You synthesize the analytical inputs from four upstream specialists:
1. HookMaster AI (0-3s attention retention)
2. AudiencePsychologist AI (cohort monologues and behavioral friction)
3. RetentionPacing AI (timeline decay and drop-off cliffs)
4. ViralAlgorithm AI (distribution ranking and loop potential)

CRITICAL CALIBRATION RULES:
- The overall creative score MUST be mathematically consistent with the upstream agents. Do NOT artificially award 75+ to a flawed video.
- Tier categories:
  * "Critical Failure / Unreleasable" (Score 1-30)
  * "High Drop-Off Risk" (Score 31-48)
  * "Average / Needs Polish" (Score 49-64)
  * "Above Average / Strong Contender" (Score 65-79)
  * "Top 5% Viral Contender" (Score 80-92)
  * "Unicorn Viral Masterpiece" (Score 93-100)
- If the creative is flawed or placeholder, declare firmly: "DO NOT PUBLISH. Immediate swipe-away risk."

Respond ONLY in valid JSON matching this schema:
{
  "overall_creative_score": <int 1-100, strictly computed>,
  "creative_tier": <"Critical Failure / Unreleasable" | "High Drop-Off Risk" | "Average / Needs Polish" | "Above Average / Strong Contender" | "Top 5% Viral Contender">,
  "executive_verdict": <string authoritative 2-3 sentence strategic summary>,
  "strengths": [
    <string primary creative strength>,
    <string secondary creative strength>
  ],
  "primary_vulnerabilities": [
    <string primary vulnerability>,
    <string secondary vulnerability>
  ],
  "prioritized_action_plan": [
    {
      "priority": <"Critical" | "High" | "Medium">,
      "timestamp": <string e.g. "00:00">,
      "issue": <string specific friction point>,
      "editorial_directive": <string exact cut, overlay, sound effect, or pacing change>,
      "predicted_roi": <string e.g. "+16% hook retention">,
      "beneficiary_cohort": <string e.g. "Casual Scroller, Impulse Explorer">
    }
  ],
  "ab_test_hypotheses": [
    {
      "variant_name": <string e.g. "Cut A: Cold Open Pattern Interrupt">,
      "hypothesis": <string why this cut could outperform the baseline>,
      "key_difference": <string exact change made>
    },
    {
      "variant_name": <string e.g. "Cut B: Social Proof / Result First">,
      "hypothesis": <string why this cut could outperform the baseline>,
      "key_difference": <string exact change made>
    }
  ],
  "publish_readiness": {
    "verdict": <"Do Not Publish (Critical Flaws)" | "Requires Hook Revision" | "Ready with Minor Polish" | "Ready to Publish">,
    "confidence_level": <"High" | "Medium" | "Provisional">,
    "estimated_retention_range": <string e.g. "12% - 22%" or "65% - 78%">
  }
}"""

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        video_title = context.get("filename", "Untitled Video")
        duration = float(context.get("duration", 24))
        platform = context.get("platform", "Instagram Reels")
        category = context.get("category", "Technology")
        
        hook_data = context.get("hook_data", {})
        audience_data = context.get("audience_data", {})
        retention_data = context.get("retention_data", {})
        algorithm_data = context.get("algorithm_data", {})

        hook_score = int(hook_data.get("hook_score", 50))
        pacing_score = int(retention_data.get("pacing_score", 50))
        alg_score = int(algorithm_data.get("algorithm_score", 50))
        
        # Calculate composite score
        composite_score = round(0.35 * hook_score + 0.35 * pacing_score + 0.30 * alg_score)

        user_prompt = f"""Synthesize the executive creative direction for:
- Title: {video_title} ({duration:.1f}s on {platform})
- HookMaster AI Score: {hook_score}/100 ({hook_data.get('verdict', 'Hook evaluation ready')})
- RetentionPacing AI Score: {pacing_score}/100 (Fatigue: {retention_data.get('cognitive_fatigue_level', 'Moderate')})
- ViralAlgorithm AI Score: {alg_score}/100
- Computed Baseline Score: {composite_score}/100

Deliver an executive verdict and actionable editorial plan that matches this score. Do NOT inflate the score."""

        if composite_score <= 30:
            fallback = {
                "overall_creative_score": composite_score,
                "creative_tier": "Critical Failure / Unreleasable",
                "executive_verdict": f"DO NOT PUBLISH. The creative exhibits fundamental flaws or placeholder assets that will cause 80%+ of mobile scrollers to swipe away in under 1 second. Algorithm distribution will stall in the cold test pool.",
                "strengths": [
                    "Correct technical file container",
                    "Ready for asset replacement"
                ],
                "primary_vulnerabilities": [
                    "Opening frames lack any engaging visual hook, human element, or pattern interrupt",
                    "Immediate swipe-away will trigger platform algorithmic distribution suppression"
                ],
                "prioritized_action_plan": [
                    {
                        "priority": "Critical",
                        "timestamp": "00:00",
                        "issue": "Opening frame is unengaging or placeholder asset.",
                        "editorial_directive": "Completely replace the opening 0-3 seconds with high-energy footage, an expressive human face, and bold on-screen captions.",
                        "predicted_roi": "+40% initial retention",
                        "beneficiary_cohort": "All cohorts (Casual Scroller, Trend Follower, Impulse Explorer)"
                    },
                    {
                        "priority": "Critical",
                        "timestamp": "00:02",
                        "issue": "Absence of clear problem statement or curiosity gap.",
                        "editorial_directive": "Add kinetic text stating the core transformation or problem being solved.",
                        "predicted_roi": "+25% completion probability",
                        "beneficiary_cohort": "Practical Buyer, Skeptical Shopper"
                    }
                ],
                "ab_test_hypotheses": [
                    {
                        "variant_name": "Cut A: Human-First Direct Address",
                        "hypothesis": "Opening with a high-energy creator addressing the camera will reduce skip rate by 35%.",
                        "key_difference": "Swaps placeholder opening for human creator hook."
                    },
                    {
                        "variant_name": "Cut B: High-Contrast Outcome First",
                        "hypothesis": "Showing the dramatic final payoff in the first 1.5 seconds will stop feed scrolling.",
                        "key_difference": "Reverse narrative order starting with the climax."
                    }
                ],
                "publish_readiness": {
                    "verdict": "Do Not Publish (Critical Flaws)",
                    "confidence_level": "High",
                    "estimated_retention_range": "10% - 22%"
                }
            }
        else:
            tier = (
                "Above Average / Strong Contender" if composite_score >= 65
                else ("Average / Needs Polish" if composite_score >= 49
                else "High Drop-Off Risk")
            )
            fallback = {
                "overall_creative_score": composite_score,
                "creative_tier": tier,
                "executive_verdict": f"The creative demonstrates functional merit, scoring {composite_score}/100. Pacing and hook require focused editorial refinement before publishing to maximize platform reach.",
                "strengths": [
                    "Clear theme and utility focus",
                    "Appeals to target analytical cohorts"
                ],
                "primary_vulnerabilities": [
                    "Opening 2 seconds can be tightened to prevent casual scroller drop-off",
                    "Mid-video transition slows narrative momentum"
                ],
                "prioritized_action_plan": [
                    {
                        "priority": "Critical",
                        "timestamp": "00:00",
                        "issue": "Opening hook needs faster pattern interrupt.",
                        "editorial_directive": "Front-load the core transformation. Trim 1.0s of setup and add kinetic captions.",
                        "predicted_roi": "+14% hook retention",
                        "beneficiary_cohort": "Casual Scroller, Impulse Explorer"
                    }
                ],
                "ab_test_hypotheses": [
                    {
                        "variant_name": "Cut A: Pain-First Pattern Interrupt",
                        "hypothesis": "Opening with an urgent problem statement will capture more casual scrollers.",
                        "key_difference": "Swaps intro for problem statistic."
                    }
                ],
                "publish_readiness": {
                    "verdict": "Ready with Minor Polish" if composite_score >= 60 else "Requires Hook Revision",
                    "confidence_level": "Medium",
                    "estimated_retention_range": f"{max(15, composite_score - 10)}% - {min(85, composite_score + 8)}%"
                }
            }

        return self.call_llm_json(user_prompt, fallback_data=fallback)
