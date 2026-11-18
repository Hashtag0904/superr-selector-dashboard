from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT / "data"
PINK, NAVY, BLUE = "#E62978", "#171C3B", "#526A9B"

st.set_page_config(page_title="SupeRR Selector | Pressure Analytics", page_icon="🏏", layout="wide")

@st.cache_data
def csv(name):
    return pd.read_csv(DATA / name)

rankings = csv("top10_rankings.csv")
bootstrap = csv("bootstrap_stability.csv")
pressure = csv("pressure_distribution.csv")
weight = csv("weight_sensitivity_overlap.csv")
gates = csv("gate_top10_overlap.csv")
prior = csv("prior_strength_sensitivity.csv")

rankings["bootstrap_pct"] = rankings["bootstrap_top10_probability"] * 100
rankings["max_share_pct"] = rankings["max_high_innings_share"] * 100
bootstrap["top10_pct"] = bootstrap["top10_probability"] * 100

st.markdown("""
<style>
.block-container{padding-top:1.15rem;max-width:1450px}
[data-testid="stSidebar"]{background:#171C3B}
[data-testid="stSidebar"] *{color:white!important}
.hero{background:linear-gradient(110deg,#171C3B 0%,#2B3159 65%,#E62978 160%);padding:1.35rem 1.6rem;border-radius:18px;color:white;margin-bottom:1rem}
.hero h1{color:white;margin:0;font-size:2rem;letter-spacing:-.03em}
.hero p{color:#F7DDE8;margin:.35rem 0 0}
.kpi{background:white;border:1px solid #E9E4EC;border-radius:14px;padding:.9rem 1rem;min-height:105px}
.kpi .label{color:#69708A;font-size:.76rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.kpi .value{color:#171C3B;font-size:1.85rem;font-weight:800;margin-top:.18rem}
.kpi .sub{color:#8A90A5;font-size:.76rem}
.section{color:#171C3B;font-weight:800;font-size:1.15rem;margin:.4rem 0 .25rem}
.note{background:#FFF0F5;border-left:4px solid #E62978;padding:.75rem .9rem;border-radius:8px;color:#4D3550}
</style>
""", unsafe_allow_html=True)

def kpi(col, label, value, sub=""):
    col.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)

def top_table(role):
    d = rankings[rankings.role.eq(role)].sort_values("rank_v21").copy()
    d["Bootstrap top-10 frequency"] = d.bootstrap_pct.map(lambda x:f"{x:.0f}%")
    d = d.rename(columns={"rank_v21":"Rank","player_name":"Player","rating_v21":"Final rating","absolute_pressure":"Absolute pressure","clutch_index":"Clutch index"})
    return d[["Rank","Player","Final rating","Absolute pressure","Clutch index","Bootstrap top-10 frequency"]].round(2)

st.sidebar.markdown("# 🏏 SUPERR SELECTOR")
st.sidebar.caption("SEASON 2 · ROUND 1")
page = st.sidebar.radio("EXPLORE", ["Overview","Player rankings","RR squad fit","Player explorer","Pressure analysis","Robustness & methodology"])
st.sidebar.divider()
st.sidebar.caption("IPL & T20I · 2022 onward")

st.markdown('<div class="hero"><h1>Pressure Performance Analytics</h1><p>Identifying players who deliver when match conditions become difficult.</p></div>', unsafe_allow_html=True)

if page == "Overview":
    st.markdown('<div class="section">The dataset and shortlist</div>',unsafe_allow_html=True)
    cs=st.columns(5)
    kpi(cs[0],"Deliveries","200,999","Source ball-by-ball rows")
    kpi(cs[1],"Matches","867","With delivery records")
    kpi(cs[2],"Eligible batters","42","Passed evidence requirements")
    kpi(cs[3],"Eligible bowlers","43","Passed evidence requirements")
    kpi(cs[4],"Bootstrap runs","150","Match-level resamples")
    left,right=st.columns([1.05,.95],gap="large")
    with left:
        st.markdown('<div class="section">Analytical workflow</div>',unsafe_allow_html=True)
        steps=["Delivery-level match state","Four pressure indices","Contextual expected outcomes","Player × match × innings aggregation","Reliability and clutch adjustment","Ranked player shortlists"]
        for i,s in enumerate(steps,1):
            st.markdown(f'<div style="display:flex;align-items:center;background:white;border:1px solid #EAE5ED;border-radius:10px;padding:.65rem .8rem;margin:.35rem 0"><span style="background:{PINK};color:white;border-radius:50%;width:26px;height:26px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;margin-right:12px">{i}</span><b style="color:{NAVY}">{s}</b></div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="section">High-pressure share by scenario</div>',unsafe_allow_html=True)
        fig=px.bar(pressure,x="scenario",y="share_ge_75_pct",color="scenario",color_discrete_sequence=[PINK,NAVY,"#F28AB4",BLUE],labels={"scenario":"Scenario","share_ge_75_pct":"Deliveries with pressure ≥75 (%)"})
        fig.update_layout(showlegend=False,margin=dict(l=8,r=8,t=12,b=10),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="note"><b>Interpretation:</b> Pressure is an adversity/urgency proxy derived from the match state before each delivery. It is not a calibrated win-probability or WPA model.</div>',unsafe_allow_html=True)
    st.markdown("The scored player pool contains 633 batter records and 473 bowler records. The displayed shortlists apply additional evidence and reliability requirements; they are not the total number of players present in the dataset.")

elif page == "Player rankings":
    st.markdown('<div class="section">Final ranked shortlists</div>',unsafe_allow_html=True)
    choice=st.radio("Role",["Batters","Bowlers"],horizontal=True)
    role="batter" if choice=="Batters" else "bowler"
    d=rankings[rankings.role.eq(role)].sort_values("rank_v21")
    st.caption("Final rating = 60% absolute pressure performance + 40% clutch improvement. Bootstrap frequency is the share of match-resamples in which the player appeared in the top 10.")
    st.dataframe(top_table(role),use_container_width=True,hide_index=True,height=450)
    fig=px.bar(d.sort_values("rating_v21"),x="rating_v21",y="player_name",orientation="h",color="rating_v21",color_continuous_scale=["#F7C4D8",PINK],labels={"rating_v21":"Final rating","player_name":"Player"})
    fig.update_layout(coloraxis_showscale=False,height=430,margin=dict(l=10,r=10,t=15,b=10),plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True)


elif page == "RR squad fit":
    targets = csv("rr_auction_targets.csv")
    st.markdown('<div class="section">Rajasthan Royals · auction squad-fit board</div>', unsafe_allow_html=True)
    st.markdown("**What the pressure shortlist can add to the retained RR core**")
    top = st.columns(4)
    kpi(top[0], "Retained squad", "19", "Confirmed for IPL 2027")
    kpi(top[1], "Open squad places", "6", "Maximum squad size: 25")
    kpi(top[2], "Overseas places left", "3", "Five overseas retained")
    kpi(top[3], "Reported purse", "₹27.05 Cr", "Before the mini-auction")
    st.markdown(
        '<div class="note"><b>Key constraint:</b> all six targets below are overseas players. RR can sign at most three overseas players in total from this watchlist, and fewer if it prioritises overseas options elsewhere. These are auction-watch candidates—not confirmed entries in the final registered auction pool.</div>',
        unsafe_allow_html=True
    )

    need_left, need_right = st.columns(2, gap="large")
    with need_left:
        st.markdown("### Batting need")
        st.markdown("""
**Hetmyer’s release leaves the clearest role gap:** a left-handed middle-order / finishing option for the No. 5–7 band.
- Existing core: Yashasvi Jaiswal, Vaibhav Sooryavanshi, Riyan Parag and Dhruv Jurel.
- Lower-order options already retained include Ravindra Jadeja, Shubham Dubey, Donovan Ferreira and Dasun Shanaka.
- The best addition should add a distinct late-innings skill, not simply another top-order batter.
""")
    with need_right:
        st.markdown("### Bowling need")
        st.markdown("""
**RR already have an experienced pace base** after bringing in Mohammed Shami, alongside Jofra Archer, Nandre Burger and Sandeep Sharma.
- Spin resources include Ravi Bishnoi, Ravindra Jadeja and Manimaran Siddharth.
- The more interesting target is therefore a complementary spin type or an all-rounder who adds batting depth—not another bowler whose role duplicates an existing specialist.
""")

    st.markdown("### Batting targets")
    st.caption("Auction-fit priority is a squad-building judgement. Pressure rank and score are kept separate from that judgement.")
    bats = targets[targets.role.eq("Batter")].sort_values("fit_priority")
    cols = st.columns(3, gap="medium")
    for col, (_, p) in zip(cols, bats.iterrows()):
        with col:
            status = "REGISTRATION PENDING"
            st.markdown(f"""
<div style="background:#fff;border:1px solid #e9dce5;border-top:5px solid #E62978;border-radius:14px;padding:14px;min-height:430px">
<div style="font-size:11px;font-weight:800;color:#E62978;letter-spacing:.08em">FIT PRIORITY {int(p.fit_priority)} · PRESSURE RANK #{int(p.model_rank)}</div>
<h3 style="color:#171C3B;margin:6px 0 2px">{p.player}</h3>
<div style="color:#6f7488;font-size:13px;font-weight:650">{p.style}</div>
<div style="display:flex;gap:8px;margin:12px 0">
 <div style="background:#FFF0F5;border-radius:8px;padding:9px;flex:1"><div style="font-size:10px;color:#6f7488">MODEL RATING</div><div style="font-size:22px;font-weight:850;color:#171C3B">{p.pressure_rating:.2f}</div></div>
 <div style="background:#F1F3F8;border-radius:8px;padding:9px;flex:1"><div style="font-size:10px;color:#6f7488">BOOTSTRAP TOP-10</div><div style="font-size:22px;font-weight:850;color:#171C3B">{p.bootstrap_top10_frequency:.0f}%</div></div>
</div>
<div style="font-size:12px;color:#E62978;font-weight:800;margin-bottom:5px">{p.rr_role}</div>
<div style="font-size:13px;color:#33394d;line-height:1.45">{p.why_it_helps}</div>
<div style="font-size:12px;color:#6f7488;line-height:1.4;margin-top:9px"><b>Trade-off:</b> {p.tradeoff}</div>
<div style="font-size:10px;color:#7b5266;font-weight:700;margin-top:10px">{status}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("### Bowling targets")
    st.caption("These are role alternatives. The shortlist is not a recommendation to buy all three.")
    bowls = targets[targets.role.eq("Bowler")].sort_values("fit_priority")
    cols = st.columns(3, gap="medium")
    for col, (_, p) in zip(cols, bowls.iterrows()):
        with col:
            st.markdown(f"""
<div style="background:#fff;border:1px solid #e9dce5;border-top:5px solid #171C3B;border-radius:14px;padding:14px;min-height:430px">
<div style="font-size:11px;font-weight:800;color:#E62978;letter-spacing:.08em">FIT PRIORITY {int(p.fit_priority)} · PRESSURE RANK #{int(p.model_rank)}</div>
<h3 style="color:#171C3B;margin:6px 0 2px">{p.player}</h3>
<div style="color:#6f7488;font-size:13px;font-weight:650">{p.style}</div>
<div style="display:flex;gap:8px;margin:12px 0">
 <div style="background:#FFF0F5;border-radius:8px;padding:9px;flex:1"><div style="font-size:10px;color:#6f7488">MODEL RATING</div><div style="font-size:22px;font-weight:850;color:#171C3B">{p.pressure_rating:.2f}</div></div>
 <div style="background:#F1F3F8;border-radius:8px;padding:9px;flex:1"><div style="font-size:10px;color:#6f7488">BOOTSTRAP TOP-10</div><div style="font-size:22px;font-weight:850;color:#171C3B">{p.bootstrap_top10_frequency:.0f}%</div></div>
</div>
<div style="font-size:12px;color:#E62978;font-weight:800;margin-bottom:5px">{p.rr_role}</div>
<div style="font-size:13px;color:#33394d;line-height:1.45">{p.why_it_helps}</div>
<div style="font-size:12px;color:#6f7488;line-height:1.4;margin-top:9px"><b>Trade-off:</b> {p.tradeoff}</div>
<div style="font-size:10px;color:#7b5266;font-weight:700;margin-top:10px">AUCTION WATCH · REGISTRATION PENDING</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("### How to use the three overseas slots")
    slot_a, slot_b, slot_c = st.columns(3)
    kpi(slot_a, "Slot 1 · Priority", "Middle-order bat", "Neesham or Chapman: choose the finishing / left-hand profile")
    kpi(slot_b, "Slot 2 · Priority", "Spin / all-round", "Raza for batting + off-spin; Theekshana for powerplay control")
    kpi(slot_c, "Slot 3 · Flex", "Best value / cover", "Hasaranga only if RR want a second attacking wrist-spinner; otherwise reserve for another gap")
    st.markdown(
        '<div class="note"><b>Practical recommendation:</b> target one genuine middle-order solution first. Then choose between an all-round off-spinner (Raza) or a specialist powerplay off-spinner (Theekshana) based on price, role availability and the final auction register. Hasaranga is a high-quality option, but his leg-spin overlaps with Ravi Bishnoi.</div>',
        unsafe_allow_html=True
    )

    with st.expander("Full shortlist and model evidence"):
        show = targets.copy()
        show["bootstrap_top10_frequency"] = show.bootstrap_top10_frequency.map(lambda x:f"{x:.1f}%")
        st.dataframe(show[["role","fit_priority","player","model_rank","pressure_rating","absolute_pressure","clutch_index","bootstrap_top10_frequency","availability"]], use_container_width=True, hide_index=True)
    st.caption("Auction status is provisional. Retention lists are published; the final registered player pool has not yet been issued. Registration was scheduled to close on 23 November, the final list is expected on 3 December, and the auction is scheduled for 16 December 2026.")
    st.markdown("**Sources:** [RR official retention announcement](https://www.rajasthanroyals.com/latest-news/ipl-2027-rr-players-retention-list-retained-released) · [IPL retention announcement](https://www.iplt20.com/news/article/tata-ipl-2027-player-retentions-announced) · [Auction timeline](https://www.wisden.com/cricket-news/ipl-2027-retention-deadline-live-updates) · [Chapman profile](https://www.cricket.com.au/players/CA%3A985/mark-chapman) · [Neesham profile](https://www.aucklandcricket.co.nz/our-teams/aces-player-profiles/james-neesham) · [Mitchell profile](https://www.cricket.com.au/players/CA%3A2242/daryl-mitchell) · [Raza profile](https://www.icc-cricket.com/rankings/25422/sikandar-raza) · [Hasaranga profile](https://www.icc-cricket.com/rankings/65027/wanindu-hasaranga) · [Theekshana profile](https://www.icc-cricket.com/rankings/69274/maheesh-theekshana)")

elif page == "Player explorer":
    st.markdown('<div class="section">Explore a shortlisted player</div>',unsafe_allow_html=True)
    choice=st.selectbox("Role",["Batter","Bowler"])
    role=choice.lower()
    d=rankings[rankings.role.eq(role)].sort_values("rank_v21")
    name=st.selectbox("Player",d.player_name.tolist())
    r=d[d.player_name.eq(name)].iloc[0]
    cs=st.columns(4)
    kpi(cs[0],"Rank",f"#{int(r.rank_v21)}",choice)
    kpi(cs[1],"Final rating",f"{r.rating_v21:.2f}","Relative index")
    kpi(cs[2],"Absolute pressure",f"{r.absolute_pressure:.2f}","60% of final rating")
    kpi(cs[3],"Clutch index",f"{r.clutch_index:.2f}","40% of final rating")
    a,b=st.columns(2,gap="large")
    with a:
        st.markdown("**Evidence by innings scenario**")
        z=pd.DataFrame({"Scenario":["First innings","Second innings"],"High pressure":[r.high_eff_innings_first,r.high_eff_innings_second],"Normal pressure":[r.normal_eff_innings_first,r.normal_eff_innings_second]})
        fig=go.Figure()
        fig.add_trace(go.Bar(name="High pressure",x=z.Scenario,y=z["High pressure"],marker_color=PINK))
        fig.add_trace(go.Bar(name="Normal pressure",x=z.Scenario,y=z["Normal pressure"],marker_color=NAVY))
        fig.update_layout(barmode="group",height=350,yaxis_title="Effective innings",margin=dict(l=10,r=10,t=15,b=10),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
    with b:
        st.markdown("**Bootstrap top-10 stability**")
        fig=go.Figure(go.Indicator(mode="gauge+number",value=float(r.bootstrap_pct),number={"suffix":"%"},gauge={"axis":{"range":[0,100]},"bar":{"color":PINK},"steps":[{"range":[0,50],"color":"#F2EEF3"},{"range":[50,100],"color":"#FCE6EF"}]}))
        fig.update_layout(height=300,margin=dict(l=15,r=15,t=25,b=5))
        st.plotly_chart(fig,use_container_width=True)
        st.caption(f"Mean bootstrap rank {r.bootstrap_mean_rank:.1f}; 10th–90th percentile rank {r.bootstrap_rank_p10:.0f}–{r.bootstrap_rank_p90:.0f}.")
    z1,z2,z3=st.columns(3)
    kpi(z1,"High-pressure effective innings",f"{r.high_eff_innings_first+r.high_eff_innings_second:.1f}","First + second innings")
    kpi(z2,"Largest innings share",f"{r.max_share_pct:.1f}%","Of high-pressure opportunities")
    kpi(z3,"Top-10 bootstrap frequency",f"{r.bootstrap_pct:.1f}%","Across 150 resamples")
    st.caption("Player explorer covers the final ranked shortlists; it does not imply that unshortlisted players were absent from the original data.")

elif page == "Pressure analysis":
    st.markdown('<div class="section">Pressure-state construction</div>',unsafe_allow_html=True)
    a,b=st.columns(2,gap="large")
    with a:
        st.markdown("**First innings · 100% index**")
        x=pd.DataFrame({"Criterion":["Par-score trajectory deficit / surplus","Wickets lost / in hand","Recent scoring deficit / burst","Recent wicket cluster / drought"],"Weight":[40,30,20,10]})
        fig=px.bar(x,x="Weight",y="Criterion",orientation="h",text="Weight",color="Weight",color_continuous_scale=["#F9B9D2",PINK])
        fig.update_layout(showlegend=False,coloraxis_showscale=False,height=310,margin=dict(l=8,r=8,t=10,b=10),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
    with b:
        st.markdown("**Second innings · 100% index**")
        x=pd.DataFrame({"Criterion":["Required-rate / chase difficulty","Wickets lost / in hand","Recent required-rate gap / momentum","Recent wickets","Late-innings urgency"],"Weight":[35,25,20,10,10]})
        fig=px.bar(x,x="Weight",y="Criterion",orientation="h",text="Weight",color="Weight",color_continuous_scale=["#F9B9D2",PINK])
        fig.update_layout(showlegend=False,coloraxis_showscale=False,height=310,margin=dict(l=8,r=8,t=10,b=10),plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True)
    cs=st.columns(3)
    kpi(cs[0],"High pressure","≥75","Included in high-pressure performance")
    kpi(cs[1],"Intermediate","51–74","Excluded from clutch comparison")
    kpi(cs[2],"Normal pressure","≤50","Comparison baseline for clutch")
    st.markdown("**Observed pressure distribution**")
    fig=px.bar(pressure,x="scenario",y="share_ge_75_pct",color="scenario",color_discrete_sequence=[PINK,NAVY,"#F28AB4",BLUE],text="share_ge_75_pct",labels={"scenario":"Scenario","share_ge_75_pct":"High-pressure deliveries (%)"})
    fig.update_traces(texttemplate="%{text:.1f}%",textposition="outside")
    fig.update_layout(showlegend=False,height=330,margin=dict(l=10,r=10,t=15,b=10),plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True)
    st.caption("State variables are evaluated before the current delivery. Recent state uses a 12-legal-ball window.")

elif page == "Robustness & methodology":
    st.markdown('<div class="section">Reliability, sensitivity and limitations</div>',unsafe_allow_html=True)
    a,b=st.columns(2,gap="large")
    with a:
        st.markdown("**Top-10 overlap when final weights change**")
        w=weight.copy();w["Role"]=w.role.map({"batter":"Batters","bowler":"Bowlers"})
        fig=px.bar(w,x="weight_pair",y="top10_overlap",color="Role",barmode="group",text="top10_overlap",color_discrete_map={"Batters":PINK,"Bowlers":NAVY},labels={"weight_pair":"Weight comparison","top10_overlap":"Players retained (out of 10)"})
        fig.update_layout(height=320,margin=dict(l=8,r=8,t=15,b=10),plot_bgcolor="white",paper_bgcolor="white",yaxis_range=[0,10.8])
        st.plotly_chart(fig,use_container_width=True)
    with b:
        st.markdown("**Top-10 overlap under alternative evidence gates**")
        g=gates.copy();g["Role"]=g.role.map({"batter":"Batters","bowler":"Bowlers"})
        g=g.rename(columns={"comparison_gate":"Evidence gate","top10_overlap_vs_recommended_v21":"Overlap (out of 10)"})
        fig=px.bar(g,x="Overlap (out of 10)",y="Evidence gate",color="Role",barmode="group",text="Overlap (out of 10)",color_discrete_map={"Batters":PINK,"Bowlers":NAVY})
        fig.update_layout(height=320,margin=dict(l=8,r=8,t=15,b=10),plot_bgcolor="white",paper_bgcolor="white",xaxis_range=[0,10.8])
        st.plotly_chart(fig,use_container_width=True)
    st.markdown("**Most stable shortlisted players in match-level bootstrap**")
    b=bootstrap.copy();b["Role"]=b.role.map({"batter":"Batters","bowler":"Bowlers"})
    b=b.sort_values("top10_probability",ascending=False).groupby("Role").head(8).sort_values(["Role","top10_probability"])
    fig=px.bar(b,x="top10_pct",y="player_name",color="Role",facet_col="Role",orientation="h",color_discrete_map={"Batters":PINK,"Bowlers":NAVY},labels={"top10_pct":"Bootstrap top-10 frequency (%)","player_name":"Player"})
    fig.update_layout(height=490,margin=dict(l=10,r=10,t=25,b=10),plot_bgcolor="white",paper_bgcolor="white",showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
    with st.expander("Detailed methodology and interpretation"):
        st.markdown("""
**Performance indices**
- Batter: 70% runs above contextual expectation per 100 weighted balls + 30% striker-dismissal avoidance.
- Bowler: 60% runs saved versus expectation per six weighted legal balls + 40% bowler-credited wickets above expectation.
- Final: 60% absolute pressure performance + 40% clutch improvement.

**Contextual expected outcomes**
- Detailed context: format × innings × phase × wickets band × pace/spin × pressure band × batting-order band.
- Sparse detailed contexts shrink towards earlier format × innings × phase priors.
- Expanding historical means exclude all observations on the same calendar date; player ID is not part of the peer baseline.

**Reliability and eligibility**
- Effective opportunities use weighted Kish ESS; each innings contributes at most one reliability unit: min(1, effective opportunities / 12).
- Player components shrink towards neutral 50 with prior strength of five effective innings.
- Eligibility: at least 3 effective high-pressure innings and 3 normal-pressure innings in each first/second-innings scenario; at least 5 high-pressure effective innings overall; at least 30 high-pressure opportunities; maximum 30% of high-pressure opportunities from one innings.
- First and second innings are equally weighted.

**Limitations**
- 702 second innings use proxy targets; unresolved extras are assigned sensitivity assumptions rather than exact recovered scores.
- 16 metadata matches have no delivery rows.
- No official innings-score reconciliation has been completed.
- The pressure index is an adversity/urgency proxy, not calibrated win probability or WPA.
- Bootstrap frequency measures stability under match resampling, not probability of objectively being the best player.
""")
    st.markdown('<div class="note"><b>Use with care:</b> innings totals have not been externally reconciled against official scorecards. Ratings are model-based estimates under the stated assumptions.</div>',unsafe_allow_html=True)

st.divider()
st.caption("SupeRR Selector Season 2 · Pressure Performance Analytics · Based on supplied historical data.")
