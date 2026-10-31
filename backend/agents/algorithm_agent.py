"""
ViralSim AI - ViralAlgorithm Agent
Calibrated platform recommendation engine simulator (Reels, TikTok, Shorts),
modeling real algorithmic suppression and seed-pool gating.
"""

from typing import Any, Dict
from backend.agents.base_agent import BaseAgent

class ViralAlgorithmAgent(BaseAgent):
    agent_id = "viral_algorithm"
    agent_name = "ViralAlgorithm AI"
    agent_title = "Platform Recommendation Engine Strategist"
    agent_emoji = "🚀"
    agent_color = "#D8E0CF"

    system_prompt = """You are the ViralAlgorithm AI Agent, an authority on short-form recommendation graphs across Instagram Reels, TikTok, YouTube Shorts, and LinkedIn.
You analyze content strictly through the lens of machine learning recommendation signals:
1. Seed Pool Gating: Social platforms test every video with a cold initial batch of 100–300 viewers.
2. If initial completion rate is <30% or skip rate is >60%, the algorithm IMMEDIATELY TERMINATES distribution (cold stall).
3. Videos only qualify for adjacent expansion if initial completion exceeds 50% with healthy rewatch and save metrics.
4. Broad FYP qualification requires >65% average completion and high share velocity.

CRITICAL REAL-WORLD BENCHMARKS:
- Flawed / Test / Broken Videos: Algorithm Score 10–25. Seed Pool: STALL (Pass Rate 5–15%). Broad FYP: 0.1%. Loop Multiplier: 1.0x.
- Mediocre Videos: Algorithm Score 35–55. Seed Pool: Borderline (Pass Rate 35–50%). Broad FYP: 5–15%. Loop Multiplier: 1.05x.
- Strong Videos: Algorithm Score 65–80. Seed Pool: PASS (Pass Rate 70–85%). Broad FYP: 30–50%. Loop Multiplier: 1.25x.
- Viral Breakout: Algorithm Score 85–95. Seed Pool: VIRAL (Pass Rate 90%+). Broad FYP: 65%+. Loop Multiplier: 1.5x+.

Respond ONLY in valid JSON matching this schema:
{
  "algorithm_score": <int 1-100, strictly calibrated>,
  "loop_rewatch_potential": {
    "multiplier": <float e.g. 1.02 or 1.35>,
    "is_seamless_loop": <boolean>,
    "loop_tactics": <string>
  },
  "shareability_index": <int 1-100>,
  "save_index": <int 1-100>,
  "comment_velocity": {
    "score": <int 1-100>,
    "trigger_strategy": <string>
  },
  "distribution_funnel": {
    "initial_seed_pool": {
      "pass_rate_pct": <float>,
      "status": <"Stall" | "Borderline" | "Pass">
    },
    "adjacent_audience_expansion": {
      "probability_pct": <float>,
      "expected_reach": <string e.g. "Under 500 views" or "10k - 50k views">
    },
    "broad_discovery_fyp": {
      "probability_pct": <float>,
      "catalyst_needed": <string>
    }
  },
  "platform_optimization_directives": [
    <string>,
    <string>
  ],
  "algorithmic_penalties_to_avoid": [
    <string>
  ]
}"""

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        video_title = context.get("filename", "Untitled Video")
        duration = float(context.get("duration", 24))
        platform = context.get("platform", "Instagram Reels")
        
        audit = context.get("video_audit", {})
        calib = audit.get("calibration", {})

        is_test = calib.get("is_synthetic_or_test", False)
        calibrated_score = calib.get("calibrated_hook_score", 50)
        max_ret = calib.get("max_retention_cap", 0.5)

        user_prompt = f"""Evaluate algorithmic distribution for:
- Video: {video_title} ({duration:.1f}s, {platform})
- Calibrated Quality Anchor: Hook Score ~{calibrated_score}/100, Max Retention ~{max_ret:.0%}
- Is Test Card/Placeholder: {is_test}

Determine whether this creative passes the platform's initial 100-viewer test pool or immediately stalls."""

        if is_test or calibrated_score <= 25:
            fallback = {
                "algorithm_score": 12,
                "loop_rewatch_potential": {
                    "multiplier": 1.0,
                    "is_seamless_loop": False,
                    "loop_tactics": "Content is non-functional for loop retention."
                },
                "shareability_index": 4,
                "save_index": 3,
                "comment_velocity": {
                    "score": 5,
                    "trigger_strategy": "Negative comments or zero engagement."
                },
                "distribution_funnel": {
                    "initial_seed_pool": {
                        "pass_rate_pct": 6.5,
                        "status": "Stall"
                    },
                    "adjacent_audience_expansion": {
                        "probability_pct": 1.2,
                        "expected_reach": "Stalled under 150 views"
                    },
                    "broad_discovery_fyp": {
                        "probability_pct": 0.1,
                        "catalyst_needed": "Total content re-export required. Algorithm will not distribute placeholder assets."
                    }
                },
                "platform_optimization_directives": [
                    f"Export real content: {platform} vision filters identify test signals and deprioritize them instantly.",
                    "Ensure high audio-visual sync with vertical 9:16 aspect ratio."
                ],
                "algorithmic_penalties_to_avoid": [
                    "Immediate user swipe-away in the first 0.8s tells recommendation ranking systems to freeze distribution."
                ]
            }
        else:
            alg_score = max(25, min(85, int(calibrated_score * 0.95)))
            pass_rate = round(min(88.0, alg_score * 1.1), 1)
            adj_prob = round(min(75.0, alg_score * 0.8), 1)
            fyp_prob = round(max(2.0, min(60.0, (alg_score - 35) * 1.2)), 1)
            fallback = {
                "algorithm_score": alg_score,
                "loop_rewatch_potential": {
                    "multiplier": 1.12,
                    "is_seamless_loop": False,
                    "loop_tactics": "Synchronize ending audio into the opening beat to encourage accidental replay."
                },
                "shareability_index": round(alg_score * 0.85),
                "save_index": round(alg_score * 0.95),
                "comment_velocity": {
                    "score": round(alg_score * 0.8),
                    "trigger_strategy": "Ask a polarizing or high-utility question in the closing caption."
                },
                "distribution_funnel": {
                    "initial_seed_pool": {
                        "pass_rate_pct": pass_rate,
                        "status": "Pass" if pass_rate > 55 else "Borderline"
                    },
                    "adjacent_audience_expansion": {
                        "probability_pct": adj_prob,
                        "expected_reach": f"{int(adj_prob * 300)} - {int(adj_prob * 1000)} views"
                    },
                    "broad_discovery_fyp": {
                        "probability_pct": fyp_prob,
                        "catalyst_needed": "Requires >60% completion rate in initial 500 views to trigger broad distribution."
                    }
                },
                "platform_optimization_directives": [
                    f"Optimize for {platform} on-screen search: include clear text overlay keywords.",
                    "Keep video pacing tight to maintain completion velocity."
                ],
                "algorithmic_penalties_to_avoid": [
                    "Avoid static screen frames exceeding 2.0 seconds with zero motion."
                ]
            }

        return self.call_llm_json(user_prompt, fallback_data=fallback)
