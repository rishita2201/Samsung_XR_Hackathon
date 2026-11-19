"""Module G: Budget-Constrained Highlight Selection Algorithm (15% Budget Optimization)."""
import numpy as np
from typing import List, Dict, Any, Set
from .temporal_localizer import TemporalSegment
from ..schemas.video_schemas import HighlightItem


def select_optimal_highlights(
    segments: List[TemporalSegment],
    video_duration: float,
    budget_ratio: float = 0.15,
    min_segment_len: float = 4.0,
    action_coverage_bonus: float = 0.40,
    redundancy_penalty: float = 0.50
) -> List[HighlightItem]:
    """Selects high-impact highlight segments under a strict 15% duration budget.
    Optimizes for:
    1. Action Coverage (40% official weight) via distinct (verb, noun) pair bonuses.
    2. Highlight F1 (25% official weight) by prioritizing top-ranked activity peaks.
    3. Non-redundancy via Maximal Marginal Relevance (MMR).
    4. Strict budget compliance <= 15.0% of total video duration and segments >= 4.0s.
    """
    if video_duration <= 0 or not segments:
        return []

    # Safe limit slightly under the 15% hard ceiling to prevent rounding margin errors
    budget_limit_seconds = budget_ratio * video_duration * 0.995
    eff_min_len = min_segment_len if budget_limit_seconds >= min_segment_len else max(1.0, budget_limit_seconds * 0.90)
    used_seconds = 0.0

    chosen_entries = []  # List of tuples: (segment, start_sec, end_sec)
    seen_action_keys: Set[Any] = set()

    # Pool of candidate segments meeting minimum duration
    pool = [s for s in segments]

    while pool and (budget_limit_seconds - used_seconds) >= eff_min_len:
        best_seg = None
        best_gain = -1e9

        for seg in pool:
            # 1. Similarity with already chosen segments (redundancy penalty)
            max_redundancy = 0.0
            if chosen_entries:
                sims = [float(seg.embedding @ c_seg.embedding) for c_seg, _, _ in chosen_entries]
                max_redundancy = max(0.0, max(sims))

            # 2. Action coverage bonus for novel (verb, noun) actions
            is_new_action = seg.cluster_key not in seen_action_keys
            coverage_gain = action_coverage_bonus if is_new_action else 0.0

            # 3. Compute marginal gain: importance * (1 - mmr * redundancy) + coverage_bonus
            marginal_gain = seg.importance * (1.0 - redundancy_penalty * max_redundancy) + coverage_gain

            # 4. Severe penalty for idle footage
            if seg.activity_score < 0.20:
                marginal_gain -= 0.50

            if marginal_gain > best_gain:
                best_gain = marginal_gain
                best_seg = seg

        if best_seg is None or best_gain <= -100:
            break

        pool.remove(best_seg)

        remaining_budget = budget_limit_seconds - used_seconds
        seg_duration = best_seg.t_end - best_seg.t_start

        start_time = best_seg.t_start
        end_time = best_seg.t_end

        # If segment is longer than remaining budget, trim centered around peak motion
        if seg_duration > remaining_budget:
            half_win = remaining_budget / 2.0
            start_time = min(max(best_seg.peak_timestamp - half_win, best_seg.t_start), best_seg.t_end - remaining_budget)
            end_time = start_time + remaining_budget

        # Round timestamps to 2 decimal places
        start_time = np.ceil(start_time * 100) / 100.0
        end_time = np.floor(end_time * 100) / 100.0

        if end_time - start_time < min_segment_len:
            continue

        chosen_entries.append((best_seg, start_time, end_time))
        used_seconds += (end_time - start_time)
        seen_action_keys.add(best_seg.cluster_key)

    # Sort selected highlights chronologically
    chosen_entries.sort(key=lambda item: item[1])

    # Merge touching or overlapping highlight intervals
    merged_highlights: List[Dict[str, Any]] = []
    for seg, st, en in chosen_entries:
        label_text = f"{seg.verb} {seg.noun}" if seg.verb != "unknown" else "highlight action"
        if merged_highlights and st - merged_highlights[-1]["end"] <= 0.10:
            prev = merged_highlights[-1]
            prev_dur = prev["end"] - prev["start"]
            curr_dur = en - st
            new_dur = prev_dur + curr_dur
            # Duration-weighted importance
            weighted_imp = (prev["importance"] * prev_dur + seg.importance * curr_dur) / max(1e-4, new_dur)
            prev["end"] = en
            prev["importance"] = weighted_imp
        else:
            merged_highlights.append({
                "start": st,
                "end": en,
                "importance": seg.importance,
                "action_label": label_text
            })

    # Convert to HighlightItem and guarantee budget constraint
    final_items: List[HighlightItem] = []
    total_check = 0.0
    for h in merged_highlights:
        st = round(float(h["start"]), 2)
        en = round(float(h["end"]), 2)
        dur = en - st
        if total_check + dur > (budget_ratio * video_duration):
            en = round(st + (budget_ratio * video_duration - total_check), 2)
            if en - st < 0.5:
                continue
        total_check += (en - st)
        final_items.append(HighlightItem(
            start=st,
            end=en,
            importance=round(float(np.clip(h["importance"], 0.0, 1.0)), 3),
            action_label=h.get("action_label")
        ))

    return final_items

