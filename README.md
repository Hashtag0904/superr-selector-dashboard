# SupeRR Selector — Pressure Performance Analytics

Interactive dashboard for the SupeRR Selector Season 2, Round 1 analysis.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy a public URL

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
2. Select this repository, branch `main`, and app file `app.py`.
3. Click **Deploy**. Streamlit will provide a shareable `*.streamlit.app` URL.

## Dashboard sections

- **Overview:** dataset coverage, analytical workflow and pressure distribution.
- **Player rankings:** searchable role-specific top-ten tables and rating charts.
- **Player explorer:** final rating, absolute-pressure score, clutch index, scenario evidence and bootstrap stability.
- **RR squad fit:** compares the pressure shortlist with Rajasthan Royals' retained squad, released-player gaps, overseas slots and role-specific auction options. Candidate registration status is clearly marked as pending until the final auction register is published.
- **Pressure analysis:** first-/second-innings criteria, weights and pressure bands.
- **Robustness & methodology:** weight sensitivity, eligibility-gate sensitivity, match-level bootstrap and limitations.

## Auction context

The RR squad-fit page uses the published IPL 2027 retention/release context. The six player names are drawn from the model's batter and bowler top tens. They are an auction-watch shortlist, not confirmed participants in the final registered auction pool. RR's reported squad position is 19 retained, six slots, three overseas slots and a reported purse of ₹27.05 crore. Recheck the auction register and any trades before acting on this analysis.

## Data included

Only compact, derived player-level rankings and aggregate diagnostics are included. The raw ball-by-ball file and source datasets are not included in this public repository.

## Interpretation notes

- Ratings are relative model indices, not official player grades.
- Bootstrap top-ten frequency measures ranking stability under match resampling; it is not the probability that a player is objectively the best.
- The pressure index is an adversity/urgency proxy, not a calibrated win-probability or WPA model.
- Some score-state inputs rely on explicit proxy assumptions for unresolved extras and second-innings targets. Official innings-score reconciliation remains outstanding.
