"""
ViralSim AI - RetentionPacing Agent
Dynamic timeline retention curve and cognitive fatigue auditor,
mathematically bound to real hook retention and visual pacing quality.
"""

from typing import Any, Dict, List
from backend.agents.base_agent import BaseAgent

class RetentionPacingAgent(BaseAgent):
    agent_id = "retention_pacing"
    agent_name = "RetentionPacing AI"
    agent_title = "Timeline & Cognitive Fatigue Auditor"
    agent_emoji = "📉"
    agent_color = "#6E8562"

    system_prompt = """You are the RetentionPacing AI Agent, an expert video editor and cognitive retention curve analyst.
You construct realistic, second-by-second retention curves grounded in the actual hook quality, visual energy, and duration of the creative.

REAL-WORLD RETENTION CURVE RULES:
1. Every short-form video starts at 1.0 (100%) at 00:00.
2. The steepest drop-off occurs between 00:00 and 00:03. By second 3, retention drops directly to the HookMaster's 0-3s retention rate.
3. For flawed or test videos: Retention plummets to 0.15-0.25 by second 2, decaying to 0.03-0.08 by the end. Pacing score is 10-25.
4. For mediocre videos: Retention drops to 0.40-0.55 by second 3, ending at 0.18-0.30 completion. Pacing score is 40-58.
5. For high-performing videos: Retention holds at 0.65-0.78 at second 3, ending at 0.45-0.62 completion. Pacing score is 70-85.
6. Do NOT invent flat 80% curves. Retention ALWAYS decays across time due to cognitive load and mobile distraction.

Respond ONLY in valid JSON matching this schema:
{
  "pacing_score": <int 1-100, strictly calibrated>,
  "cognitive_fatigue_level": <"Extreme Drop-Off" | "High" | "Moderate" | "Low">,
  "average_watch_percentage": <float e.g. 18.2 or 62.5>,
  "retention_curve": [
    {
      "seconds": <float>,
      "timestamp": <string e.g. "00:00">,
      "retention": <float 0.0-1.0>,
      "energy_state": <"Peak" | "Steep Cliff" | "Dip" | "Steady" | "Climax">,
      "editorial_note": <string brief audit of what is happening on screen>
    }
  ],
  "drop_off_cliffs": [
    {
      "timestamp": <string e.g. "00:02">,
      "severity": <"Critical" | "Moderate" | "Minor">,
      "cause": <string reason for drop-off>,
      "fix": <string exact edit to eliminate the cliff>
    }
  ],
  "pacing_verdict": <string blunt high-level diagnosis of rhythm and retention flow>
}"""

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        video_title = context.get("filename", "Untitled Video")
        duration = float(context.get("duration", 24))
        platform = context.get("platform", "Instagram Reels")
        
        audit = context.get("video_audit", {})
        vision = audit.get("vision", {})
        calib = audit.get("calibration", {})

        is_test = calib.get("is_synthetic_or_test", False)
        calibrated_score = calib.get("calibrated_hook_score", 50)
        max_ret = calib.get("max_retention_cap", 0.5)

        user_prompt = f"""Construct an uncompromising, mathematically realistic retention curve for:
- Video: {video_title} ({duration:.1f}s on {platform})
- Visual Hook Reality: {vision.get('primary_visual_subject', 'Standard footage')}
- Visual Hook Score: {vision.get('visual_hook_score_1_to_10', 5)}/10
- Visual Defects: {vision.get('objective_visual_flaws', [])}
- Estimated 0-3s Retention Anchor: Approximately {max_ret:.0%}
- Is Placeholder/Test Card: {is_test}

Generate exactly 11 retention points from 00:00 to the end. The curve MUST start at 1.0 (100%) at 00:00 and reflect steep drop-off at second 2 if the hook is weak or test footage."""

        # Mathematically grounded fallback curve
        retention_points = []
        base_anchor = max_ret if not is_test else 0.18
        pacing_score = max(10, min(85, int(calibrated_score * 0.95)))

        for i in range(11):
            t = duration * i / 10.0
            if i == 0:
                ret = 1.0
                energy = "Peak"
                note = "Initial feed impression"
            elif i == 1:
                # Steep drop-off at 10% of duration (second 1.5 - 2)
                ret = round(base_anchor + 0.08, 3)
                energy = "Steep Cliff" if is_test or base_anchor < 0.4 else "Steady"
                note = "Opening hook evaluation window"
            else:
                # Continuous exponential decay
                decay_factor = ((i - 1) / 9.0) * (base_anchor * 0.70)
                ret = round(max(0.03, base_anchor - decay_factor), 3)
                energy = "Climax" if i == 10 else ("Dip" if i in (4, 7) else "Steady")
                note = "Demonstration phase" if i < 7 else ("Value synthesis" if i < 9 else "Call to action")

            retention_points.append({
                "seconds": round(t, 1),
                "timestamp": f"{int(t // 60):02d}:{int(t % 60):02d}",
                "retention": ret,
                "energy_state": energy,
                "editorial_note": note
            })

        avg_pct = round(sum(p["retention"] for p in retention_points) / len(retention_points) * 100, 1)

        fallback = {
            "pacing_score": pacing_score,
            "cognitive_fatigue_level": "Extreme Drop-Off" if is_test or base_anchor < 0.3 else ("Moderate" if base_anchor < 0.6 else "Low"),
            "average_watch_percentage": avg_pct,
            "retention_curve": retention_points,
            "drop_off_cliffs": [
                {
                    "timestamp": f"{int(min(2.0, duration * 0.15) // 60):02d}:{int(min(2.0, duration * 0.15) % 60):02d}",
                    "severity": "Critical" if is_test or base_anchor < 0.4 else "Moderate",
                    "cause": "Opening visual fails to establish immediate curiosity, triggering instant feed scroll.",
                    "fix": "Start with an energetic pattern interrupt and high-contrast captions within the first 1.0 second."
                }
            ],
            "pacing_verdict": f"The creative experiences an immediate drop to {base_anchor:.0%} retention within the opening seconds. Average watch completion is {retention_points[-1]['retention']:.0%}."
        }

        return self.call_llm_json(user_prompt, fallback_data=fallback)
