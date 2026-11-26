import time

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="OS Simulator", page_icon="🖥️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1200px;}
button[data-baseweb="tab"] p {font-size: 1.05rem; font-weight: 600;}
div[data-testid="stMetric"] {background: rgba(128,128,128,0.12); padding: 12px 16px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.title("🖥️ OS Simulator")
st.caption("Interactive CPU scheduling, page replacement, and deadlock avoidance (Banker's algorithm)")


def is_dark():
    try:
        return st.context.theme.type != "light"
    except Exception:
        return True


# =====================================================================
# CPU SCHEDULING ALGORITHMS (each returns a timeline of (name, start, end))
# =====================================================================
def fcfs(procs):
    t, timeline = 0, []
    for p in sorted(procs, key=lambda x: x["at"]):
        t = max(t, p["at"])
        timeline.append((p["name"], t, t + p["bt"]))
        t += p["bt"]
    return timeline


def sjf(procs):
    """Non-preemptive Shortest Job First."""
    todo = sorted(procs, key=lambda x: x["at"])
    t, timeline = 0, []
    while todo:
        ready = [p for p in todo if p["at"] <= t]
        if not ready:
            t = todo[0]["at"]
            continue
        p = min(ready, key=lambda x: (x["bt"], x["at"]))
        timeline.append((p["name"], t, t + p["bt"]))
        t += p["bt"]
        todo.remove(p)
    return timeline


def round_robin(procs, q):
    remaining = {p["name"]: p["bt"] for p in procs}
    pending = sorted(procs, key=lambda x: x["at"])
    queue, timeline, t = [], [], 0
    while pending or queue:
        while pending and pending[0]["at"] <= t:
            queue.append(pending.pop(0)["name"])
        if not queue:
            t = pending[0]["at"]
            continue
        name = queue.pop(0)
        run = min(q, remaining[name])
        timeline.append((name, t, t + run))
        t += run
        remaining[name] -= run
        while pending and pending[0]["at"] <= t:
            queue.append(pending.pop(0)["name"])
        if remaining[name] > 0:
            queue.append(name)
    return timeline


def cpu_metrics(procs, timeline):
    finish = {}
    for name, s, e in timeline:
        finish[name] = e
    rows = []
    for p in procs:
        tat = finish[p["name"]] - p["at"]
        rows.append({"Process": p["name"], "Turnaround": tat, "Waiting": tat - p["bt"]})
    avg_wait = sum(r["Waiting"] for r in rows) / len(rows)
    avg_tat = sum(r["Turnaround"] for r in rows) / len(rows)
    switches = sum(1 for a, b in zip(timeline, timeline[1:]) if a[0] != b[0])
    return rows, avg_wait, avg_tat, switches


def draw_gantt(timeline, color_of, upto=None, placeholder=None):
    """Draw the Gantt chart. If upto is given, draw only what happened before that time."""
    fg = "white" if is_dark() else "#222222"
    total = timeline[-1][2]
    fig, ax = plt.subplots(figsize=(10, 1.9))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    for name, s_, e_ in timeline:
        if upto is not None:
            if s_ >= upto:
                continue
            e_ = min(e_, upto)
        ax.barh(0, e_ - s_, left=s_, color=color_of[name], edgecolor="none", height=0.7)
        ax.text((s_ + e_) / 2, 0, name, ha="center", va="center", color="white",
                fontsize=9, fontweight="bold")
    if upto is not None:
        ax.axvline(upto, color="#FFD54F", lw=2)
    ax.set_xlim(0, total)
    ax.set_yticks([])
    ticks = sorted({a for _, a, _ in timeline} | {total})
    ax.set_xticks(ticks)
    ax.tick_params(colors=fg)
    ax.set_xlabel("Time", color=fg)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(fg)
    (placeholder or st).pyplot(fig)
    plt.close(fig)


# =====================================================================
# PAGE REPLACEMENT ALGORITHMS
# =====================================================================
def simulate_pages(refs, n, algo):
    """Returns one step per reference: page, frame contents, hit?, evicted page."""
    slots = [None] * n
    loaded_at, last_used, steps = {}, {}, []
    for i, page in enumerate(refs):
        hit = page in slots
        evicted = None
        if not hit:
            if None in slots:
                idx = slots.index(None)
            else:
                if algo == "FIFO":
                    victim = min(slots, key=lambda p: loaded_at[p])
                elif algo == "LRU":
                    victim = min(slots, key=lambda p: last_used[p])
                else:  # Optimal: evict the page used farthest in the future
                    def next_use(p):
                        try:
                            return refs.index(p, i + 1)
                        except ValueError:
                            return float("inf")
                    victim = max(slots, key=next_use)
                idx = slots.index(victim)
                evicted = victim
            slots[idx] = page
            loaded_at[page] = i
        last_used[page] = i
        steps.append({"page": page, "slots": slots.copy(), "hit": hit, "evicted": evicted})
    return steps


def show_page_table(steps, n):
    cols = [f"t{i+1}" for i in range(len(steps))]
    data = {"Page": [s["page"] for s in steps]}
    for f in range(n):
        data[f"Frame {f+1}"] = [("-" if s["slots"][f] is None else s["slots"][f]) for s in steps]
    data["Result"] = ["HIT" if s["hit"] else "FAULT" for s in steps]
    df = pd.DataFrame.from_dict(data, orient="index", columns=cols).astype(str)

    def style(d):
        out = pd.DataFrame("", index=d.index, columns=d.columns)
        for c in d.columns:
            if d.loc["Result", c] == "HIT":
                out.loc["Result", c] = "background-color:#2e7d32;color:white;font-weight:bold"
            else:
                out.loc["Result", c] = "background-color:#c62828;color:white;font-weight:bold"
            out.loc["Page", c] = "font-weight:bold"
        return out

    st.dataframe(df.style.apply(style, axis=None), width="stretch")


# =====================================================================
# UI
# =====================================================================
tab_cpu, tab_page, tab_bank = st.tabs(["CPU Scheduling", "Page Replacement", "Banker's Algorithm"])

# ---------------------------- CPU tab -------------------------------
with tab_cpu:
    mode = st.radio("Mode", ["Single algorithm", "Compare all"], horizontal=True, key="cpu_mode")
    quantum = st.number_input("Round Robin time quantum", 1, 20, 2)
    if mode == "Single algorithm":
        algo = st.selectbox("Algorithm", ["FCFS", "SJF", "Round Robin"])
        ac1, ac2 = st.columns([1, 2])
        animate = ac1.checkbox("Animate Gantt chart")
        speed = ac2.slider("Animation speed", 1, 5, 3)

    n = st.number_input("Number of processes", 1, 10, 4)
    procs = []
    for i in range(n):
        c1, c2 = st.columns(2)
        at = c1.number_input(f"P{i+1} arrival", 0, 50, i, key=f"a{i}")
        bt = c2.number_input(f"P{i+1} burst", 1, 50, 3 + i, key=f"b{i}")
        procs.append({"name": f"P{i+1}", "at": at, "bt": bt})

    cmap = plt.get_cmap("tab10")
    color_of = {p["name"]: cmap(i % 10) for i, p in enumerate(procs)}

    def run_algo(name):
        if name == "FCFS":
            return fcfs(procs)
        if name == "SJF":
            return sjf(procs)
        return round_robin(procs, quantum)

    if st.button("Run", type="primary", key="cpu_run"):
        if mode == "Single algorithm":
            tl = run_algo(algo)
            rows, avg_wait, avg_tat, switches = cpu_metrics(procs, tl)
            ph = st.empty()
            if animate:
                total = tl[-1][2]
                for t in range(total + 1):
                    draw_gantt(tl, color_of, upto=t, placeholder=ph)
                    time.sleep(0.5 / speed)
            draw_gantt(tl, color_of, placeholder=ph)
            st.table(rows)
            c1, c2, c3 = st.columns(3)
            c1.metric("Avg waiting", f"{avg_wait:.2f}")
            c2.metric("Avg turnaround", f"{avg_tat:.2f}")
            c3.metric("Context switches", switches)
        else:
            summary = []
            for name in ["FCFS", "SJF", "Round Robin"]:
                tl = run_algo(name)
                rows, avg_wait, avg_tat, switches = cpu_metrics(procs, tl)
                st.subheader(name)
                draw_gantt(tl, color_of)
                summary.append({
                    "Algorithm": name,
                    "Avg waiting": round(avg_wait, 2),
                    "Avg turnaround": round(avg_tat, 2),
                    "Context switches": switches,
                })
            st.subheader("Comparison")
            st.table(summary)
            best_val = min(r["Avg waiting"] for r in summary)
            winners = [r["Algorithm"] for r in summary if r["Avg waiting"] == best_val]
            if len(winners) > 1:
                st.success(f"Tie for lowest average waiting time ({best_val}): {', '.join(winners)}")
            else:
                st.success(f"Lowest average waiting time: {winners[0]} ({best_val})")
            st.caption("SJF minimizes average waiting time but can starve long jobs. "
                       "Round Robin is fairer and gives better response time, at the cost of more context switches.")

# ------------------------ Page replacement tab ----------------------
with tab_page:
    pmode = st.radio("Mode", ["Single algorithm", "Compare all"], horizontal=True, key="pg_mode")
    ref_text = st.text_input("Reference string (space or comma separated)",
                             "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1")
    frames = st.number_input("Number of frames", 1, 10, 3)
    if pmode == "Single algorithm":
        palgo = st.selectbox("Algorithm", ["FIFO", "LRU", "Optimal"], key="pg_algo")

    if st.button("Run", type="primary", key="pg_run"):
        refs = ref_text.replace(",", " ").split()
        if not refs:
            st.warning("Enter a reference string first.")
        elif pmode == "Single algorithm":
            steps = simulate_pages(refs, frames, palgo)
            faults = sum(1 for s in steps if not s["hit"])
            show_page_table(steps, frames)
            c1, c2, c3 = st.columns(3)
            c1.metric("Page faults", faults)
            c2.metric("Hits", len(refs) - faults)
            c3.metric("Hit ratio", f"{(len(refs) - faults) / len(refs):.0%}")
        else:
            summary = []
            for name in ["FIFO", "LRU", "Optimal"]:
                steps = simulate_pages(refs, frames, name)
                faults = sum(1 for s in steps if not s["hit"])
                st.subheader(name)
                show_page_table(steps, frames)
                summary.append({
                    "Algorithm": name,
                    "Page faults": faults,
                    "Hit ratio": f"{(len(refs) - faults) / len(refs):.0%}",
                })
            st.subheader("Comparison")
            st.table(summary)
            st.bar_chart(pd.DataFrame(summary).set_index("Algorithm")["Page faults"])
            best_val = min(r["Page faults"] for r in summary)
            winners = [r["Algorithm"] for r in summary if r["Page faults"] == best_val]
            st.success(f"Fewest page faults ({best_val}): {', '.join(winners)}")
            st.caption("Optimal is the theoretical best (it needs future knowledge), "
                       "so real algorithms like LRU and FIFO are judged against it.")


# ------------------------ Banker's algorithm tab --------------------
def safety_check(avail, alloc, need):
    """Returns (is_safe, safe_sequence, steps, stuck_processes)."""
    n = len(alloc)
    work = avail[:]
    done = [False] * n
    seq, steps = [], []
    while True:
        found = False
        for i in range(n):
            if not done[i] and all(need[i][j] <= work[j] for j in range(len(work))):
                before = work[:]
                work = [work[j] + alloc[i][j] for j in range(len(work))]
                steps.append({
                    "Step": len(seq) + 1,
                    "Process": f"P{i}",
                    "Need": str(need[i]),
                    "Work before": str(before),
                    "Work after": str(work),
                })
                done[i] = True
                seq.append(f"P{i}")
                found = True
                break
        if not found:
            break
    stuck = [f"P{i}" for i in range(n) if not done[i]]
    return len(stuck) == 0, seq, steps, stuck


BANK_ALLOC = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
BANK_MAX = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
BANK_AVAIL = [[3, 3, 2]]

with tab_bank:
    c1, c2 = st.columns(2)
    nb = c1.number_input("Number of processes", 1, 8, 5, key="bk_n")
    mb = c2.number_input("Number of resource types", 1, 5, 3, key="bk_m")
    res_names = [chr(65 + j) for j in range(mb)]
    proc_names = [f"P{i}" for i in range(nb)]

    def default_df(mat, rows, idx):
        data = [[mat[i][j] if i < len(mat) and j < len(mat[i]) else 0 for j in range(mb)]
                for i in range(rows)]
        return pd.DataFrame(data, index=idx, columns=res_names)

    st.caption("Edit the tables below. Results update automatically. Defaults are the classic textbook example.")
    ca, cm = st.columns(2)
    with ca:
        st.write("**Allocation** (currently held)")
        alloc_df = st.data_editor(default_df(BANK_ALLOC, nb, proc_names), key=f"bk_alloc_{nb}_{mb}")
    with cm:
        st.write("**Max** (maximum claim)")
        max_df = st.data_editor(default_df(BANK_MAX, nb, proc_names), key=f"bk_max_{nb}_{mb}")
    st.write("**Available** (free resources)")
    avail_df = st.data_editor(default_df(BANK_AVAIL, 1, ["Available"]), key=f"bk_avail_{nb}_{mb}")

    alloc = [[int(x) for x in row] for row in alloc_df.values.tolist()]
    maxm = [[int(x) for x in row] for row in max_df.values.tolist()]
    avail = [int(x) for x in avail_df.values.tolist()[0]]
    need = [[maxm[i][j] - alloc[i][j] for j in range(mb)] for i in range(nb)]

    if any(v < 0 for row in need for v in row):
        st.error("Invalid input: some process has Allocation greater than Max. Fix the tables.")
    else:
        st.write("**Need** = Max - Allocation")
        st.dataframe(pd.DataFrame(need, index=proc_names, columns=res_names))

        safe, seq, steps, stuck = safety_check(avail, alloc, need)
        st.subheader("Safety check")
        if steps:
            st.table(steps)
        if safe:
            st.success("SAFE state. Safe sequence: " + " → ".join(seq))
        else:
            st.error("UNSAFE state. Deadlock is possible. These processes can never finish: "
                     + ", ".join(stuck))

        st.subheader("Resource request")
        r1, r2 = st.columns([1, 3])
        who = r1.selectbox("Process", list(range(nb)), format_func=lambda i: f"P{i}", key="bk_who")
        req_cols = r2.columns(mb)
        req = [req_cols[j].number_input(f"Request {res_names[j]}", 0, 50, 0, key=f"bk_req_{j}")
               for j in range(mb)]
        if st.button("Check request", key="bk_req_btn"):
            if any(req[j] > need[who][j] for j in range(mb)):
                st.error(f"Denied: P{who} is asking for more than its maximum claim.")
            elif any(req[j] > avail[j] for j in range(mb)):
                st.warning(f"P{who} must wait: not enough resources available right now.")
            else:
                t_avail = [avail[j] - req[j] for j in range(mb)]
                t_alloc = [row[:] for row in alloc]
                t_need = [row[:] for row in need]
                for j in range(mb):
                    t_alloc[who][j] += req[j]
                    t_need[who][j] -= req[j]
                ok, t_seq, _, _ = safety_check(t_avail, t_alloc, t_need)
                if ok:
                    st.success(f"Request can be GRANTED. New safe sequence: " + " → ".join(t_seq))
                else:
                    st.error("Request DENIED: granting it would lead to an unsafe state.")
