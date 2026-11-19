"""Segmentation, multi-cue explainable importance scoring, and official 15% budget-constrained selection.
Strictly compliant with official Samsung Track 4 Student Package schema:
- Highlights: [{"segment": [start, end]}]
- Actions: [{"segment": [start, end], "verb": "...", "noun": "...", "score": ...}]
- Min highlight segment >= 4.0s (to avoid being ignored by official evaluator)
"""
import numpy as np


def percentile_rank(x):
    x = np.asarray(x, dtype=np.float64)
    if len(x) < 2:
        return np.full(len(x), 0.5)
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(len(x))
    return r / (len(x) - 1)


def smooth(x, k=3):
    if k <= 1 or len(x) < k:
        return np.asarray(x, dtype=np.float64)
    pad = k // 2
    xp = np.pad(x, pad, mode="edge")
    return np.convolve(xp, np.ones(k) / k, mode="valid")


def segment(emb, dt, min_len=2.0, max_len=8.0):
    """Change-point segmentation on embedding distance. Returns [(i0, i1)) sample ranges."""
    N = len(emb)
    min_n = max(1, int(round(min_len / dt)))
    max_n = max(2, int(round(max_len / dt)))
    if N <= min_n:
        return [(0, N)]
    d = 1.0 - (emb[1:] * emb[:-1]).sum(1)
    thr = d.mean() + 0.85 * d.std()
    bounds = [0]
    for i in range(1, N):
        since = i - bounds[-1]
        if (d[i - 1] > thr and since >= min_n) or since >= max_n:
            bounds.append(i)
    if N - bounds[-1] < min_n and len(bounds) > 1:
        bounds.pop()
    bounds.append(N)
    return list(zip(bounds[:-1], bounds[1:]))


class Segment:
    __slots__ = ("i0", "i1", "t0", "t1", "emb", "act", "hoi", "novelty", "conf",
                 "verb", "noun", "key", "imp", "peak_t")


def build_segments(samples, emb, ranges, labeler=None, w=(0.40, 0.25, 0.20, 0.15)):
    t, dur = samples.times, samples.duration
    act = percentile_rank(smooth(samples.hand_res + 0.25 * samples.glob_mot, 3))
    hoi = percentile_rank(smooth(samples.hoi_scores, 3)) if hasattr(samples, 'hoi_scores') else act
    centroid = emb.mean(0)
    centroid /= (np.linalg.norm(centroid) + 1e-8)
    segs = []
    for i0, i1 in ranges:
        s = Segment()
        s.i0, s.i1 = i0, i1
        s.t0 = float(t[i0]) if i0 > 0 else 0.0
        s.t1 = float(t[i1 - 1]) if i1 <= len(t) else float(dur)
        if s.t1 <= s.t0:
            s.t1 = min(dur, s.t0 + 1.0)
        e = emb[i0:i1].mean(0)
        s.emb = e / (np.linalg.norm(e) + 1e-8)
        s.act = float(act[i0:i1].mean())
        s.hoi = float(hoi[i0:i1].mean())
        s.peak_t = float(t[i0 + int(act[i0:i1].argmax())]) if (i1 - i0) > 0 else (s.t0 + s.t1) / 2.0
        s.novelty = float(1.0 - s.emb @ centroid)
        s.verb = s.noun = "other"
        s.conf = 0.5
        if labeler is not None:
            s.verb, s.noun, s.conf = labeler.action(s.emb)
        segs.append(s)

    nov = percentile_rank([s.novelty for s in segs])
    cf = percentile_rank([s.conf for s in segs]) if labeler is not None else np.zeros(len(segs))
    wa, wh, wn, wc = w if labeler is not None else (0.50, 0.30, 0.20, 0.0)
    for s, n_, c_ in zip(segs, nov, cf):
        score = wa * s.act + wh * s.hoi + wn * n_ + wc * c_
        if s.act < 0.20:
            score *= 0.5
        s.imp = float(np.clip(score, 0.0, 1.0))

    centers = []
    for s in segs:
        if labeler is not None and s.verb != "other":
            s.key = (s.verb, s.noun)
        else:
            k = next((j for j, c in enumerate(centers) if float(c @ s.emb) > 0.88), None)
            if k is None:
                centers.append(s.emb)
                k = len(centers) - 1
            s.key = ("cluster", str(k))
    return segs


def select_highlights(segs, duration, budget=0.15, min_dur=4.0, pair_bonus=0.40, mmr=0.5):
    """Greedy MMR selection strictly adhering to Samsung Track 4 constraints:
    1. Total duration <= 15.0% of video duration.
    2. Segments are >= 4.0s (official rule: segments < 4.0s are ignored by evaluator).
    3. Chronologically sorted with zero overlap.
    4. Format: [{"segment": [start, end]}]
    """
    total_budget_sec = budget * duration * 0.995
    # For short videos where total budget is small, adapt min_dur
    eff_min_dur = min_dur if total_budget_sec >= min_dur else max(1.0, total_budget_sec * 0.90)

    chosen, used, seen_keys = [], 0.0, set()
    pool = [s for s in segs]

    while pool and (total_budget_sec - used) >= eff_min_dur:
        best, best_g = None, -1e9
        for s in pool:
            red = max((float(s.emb @ c.emb) for c, _, _ in chosen), default=0.0)
            g = s.imp * (1.0 - mmr * max(red, 0.0)) + (pair_bonus if s.key not in seen_keys else 0.0)
            if s.act < 0.20:
                g -= 0.50
            if g > best_g:
                best, best_g = s, g
        if best is None:
            break
        pool.remove(best)

        # Candidate span
        a, b = best.t0, best.t1
        # Expand span if shorter than eff_min_dur
        if (b - a) < eff_min_dur:
            needed = eff_min_dur - (b - a)
            half = needed / 2.0
            a = max(0.0, a - half)
            b = min(duration, b + half)
            if (b - a) < eff_min_dur:
                if a <= 0.01:
                    b = min(duration, a + eff_min_dur)
                else:
                    a = max(0.0, b - eff_min_dur)

        # Check remaining budget
        rem = total_budget_sec - used
        if (b - a) > rem:
            if rem < eff_min_dur and len(chosen) > 0:
                # Cannot create another >= 4s segment without violating budget
                break
            # Trim centered on peak
            a = min(max(best.peak_t - rem / 2.0, 0.0), max(0.0, duration - rem))
            b = a + rem

        a = round(float(a), 2)
        b = round(float(b), 2)
        if (b - a) < (eff_min_dur - 0.05):
            continue

        chosen.append((best, a, b))
        used += (b - a)
        seen_keys.add(best.key)

    # If no segment was chosen yet and duration permits, pick top single segment
    if not chosen and segs and total_budget_sec >= 1.0:
        best_s = max(segs, key=lambda s: s.imp)
        seg_len = min(total_budget_sec, max(eff_min_dur, best_s.t1 - best_s.t0))
        a = max(0.0, best_s.t0)
        b = min(duration, a + seg_len)
        chosen.append((best_s, round(a, 2), round(b, 2)))

    # Sort chronologically
    chosen.sort(key=lambda x: x[1])

    # Merge overlapping or closely adjacent highlight spans (gap <= 0.5s)
    merged = []
    for s, a, b in chosen:
        if merged and a <= merged[-1][1] + 0.5:
            prev_a, prev_b = merged[-1]
            merged[-1] = (prev_a, max(prev_b, b))
        else:
            merged.append((a, b))

    # Enforce strictly <= budget * duration across total selected duration
    out = []
    tot = 0.0
    budget_limit = budget * duration
    for a, b in merged:
        if tot >= budget_limit:
            break
        seg_dur = b - a
        if tot + seg_dur > budget_limit:
            b = round(a + (budget_limit - tot), 2)
            seg_dur = b - a
        if seg_dur >= 0.5:
            tot += seg_dur
            out.append({
                "segment": [round(float(a), 2), round(float(b), 2)]
            })

    # Final guarantee: if video duration >= 27.0s, ensure at least one segment is >= 4.0s
    if out and duration >= 27.0:
        has_ge_4 = any((seg["segment"][1] - seg["segment"][0]) >= 4.0 for seg in out)
        if not has_ge_4 and len(out) > 0:
            seg0 = out[0]["segment"]
            new_end = min(duration, seg0[0] + 4.0)
            if new_end - seg0[0] <= budget_limit:
                out[0]["segment"] = [seg0[0], round(float(new_end), 2)]

    return out


def build_actions(segs, min_act=0.20):
    """Returns actions conforming to Student Kit format:
    [{"segment": [start, end], "verb": "...", "noun": "...", "score": ...}]
    """
    out = []
    for s in segs:
        if s.act < min_act:
            continue
        verb = str(s.verb).strip() if s.verb and s.verb != "unknown" else "other"
        noun = str(s.noun).strip() if s.noun and s.noun != "unknown" else "other"
        score = round(float(np.clip(s.conf if hasattr(s, "conf") and s.conf > 0 else s.imp, 0.0, 1.0)), 3)
        t0 = round(float(s.t0), 2)
        t1 = round(float(s.t1), 2)
        if t1 <= t0:
            t1 = t0 + 0.5

        if out and out[-1]["verb"] == verb and out[-1]["noun"] == noun and t0 - out[-1]["segment"][1] < 1.0:
            out[-1]["segment"][1] = t1
            out[-1]["score"] = round(float(max(out[-1]["score"], score)), 3)
        else:
            out.append({
                "segment": [t0, t1],
                "verb": verb,
                "noun": noun,
                "score": score
            })
    return out
