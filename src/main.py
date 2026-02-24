import json
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from datetime import datetime
from collections import defaultdict
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

EARTH_RADIUS_M = 6371000  # meters


class AdvancedContactTracing:
    def __init__(self, data_file, status_file="covid_status.json"):
        self.data_file = data_file
        self.status_file = status_file
        self.data = self.load_data()
        self.coords = self.prepare_coords()
        self.covid_status = self.init_covid_status()

    def load_data(self):
        with open(self.data_file, "r") as f:
            return json.load(f)

    def prepare_coords(self):
        return np.array([
            [float(r["latitude"]), float(r["longitude"])]
            for r in self.data
        ])

    def init_covid_status(self):
        people = {r["id"] for r in self.data}
        return {
            p: {"status": "safe", "date": None, "risk_score": 0}
            for p in people
        }

    def mark_covid_case(self, person):
        self.covid_status[person] = {
            "status": "positive",
            "date": datetime.now().isoformat(),
            "risk_score": 100,
        }
        self.save_status()

    def calculate_risk_propagation(
        self,
        contact_radius_m=50,
        min_samples=3,
    ):
        # Reset everyone except positives
        for p in self.covid_status:
            if self.covid_status[p]["status"] != "positive":
                self.covid_status[p].update(
                    {"status": "safe", "risk_score": 0}
                )

        # --- DBSCAN ---
        eps_rad = contact_radius_m / EARTH_RADIUS_M
        coords_rad = np.radians(self.coords)

        labels = DBSCAN(
            eps=eps_rad,
            min_samples=min_samples,
            metric="haversine",
        ).fit_predict(coords_rad)

        # --- Build cluster → people mapping ---
        clusters = defaultdict(set)
        for idx, label in enumerate(labels):
            if label != -1:
                clusters[label].add(self.data[idx]["id"])

        positive_people = {
            p for p, s in self.covid_status.items()
            if s["status"] == "positive"
        }

        # --- PERSON-CENTRIC propagation ---
        for people in clusters.values():
            infected = people & positive_people
            if not infected:
                continue  # 🔥 critical fix

            risk = len(infected) / len(people) * 100

            for p in people:
                if self.covid_status[p]["status"] != "positive":
                    self.covid_status[p]["risk_score"] = max(
                        self.covid_status[p]["risk_score"], risk
                    )
                    self.covid_status[p]["status"] = (
                        "high_risk" if risk >= 50 else "low_risk"
                    )

        return labels

    def get_cluster_info(self, contact_radius_m=50, min_samples=3):
        """Get detailed cluster information for debugging"""
        eps_rad = contact_radius_m / EARTH_RADIUS_M
        coords_rad = np.radians(self.coords)
        
        labels = DBSCAN(
            eps=eps_rad,
            min_samples=min_samples,
            metric="haversine",
        ).fit_predict(coords_rad)
        
        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            person = self.data[idx]["id"]
            clusters[label].append(person)
        
        return clusters, labels

    def get_dashboard_stats(self):
        s = pd.Series(
            [v["status"] for v in self.covid_status.values()]
        ).value_counts()

        return {
            "total_people": len(self.covid_status),
            "positive": s.get("positive", 0),
            "high_risk": s.get("high_risk", 0),
            "low_risk": s.get("low_risk", 0),
            "safe": s.get("safe", 0),
        }

    def save_status(self):
        with open(self.status_file, "w") as f:
            json.dump(self.covid_status, f, indent=2)

    def load_status(self):
        try:
            with open(self.status_file, "r") as f:
                self.covid_status.update(json.load(f))
        except FileNotFoundError:
            pass


# ===================== DASHBOARD =====================

def run_dashboard():
    st.set_page_config("COVID Contact Tracing", layout="wide")
    st.sidebar.title("🚨 Control Panel")

    tracer = AdvancedContactTracing("data/data.json", "data/covid_status.json")
    tracer.load_status()

    st.sidebar.subheader("Mark COVID Case")
    
    person = st.sidebar.selectbox(
        "Select Person",
        sorted(tracer.covid_status.keys())
    )

    if st.sidebar.button("Mark COVID+"):
        tracer.mark_covid_case(person)
        st.sidebar.success(f"{person} marked COVID+")
    
    st.sidebar.subheader("Risk Analysis Settings")
    contact_radius = st.sidebar.slider(
        "Contact Radius (meters)",
        min_value=10,
        max_value=500,
        value=50,
        step=10,
        help="Distance threshold for contact detection"
    )
    min_samples = st.sidebar.slider(
        "Min Cluster Size",
        min_value=2,
        max_value=10,
        value=3,
        help="Minimum people needed to form a cluster"
    )

    if st.sidebar.button("Run Risk Analysis"):
        labels = tracer.calculate_risk_propagation(
            contact_radius_m=contact_radius,
            min_samples=min_samples
        )
        tracer.save_status()
        st.sidebar.success("Risk propagation complete")

    # -------- MAIN DASHBOARD --------
    st.title("🦠 COVID Contact Tracing Dashboard")
    
    # Show currently marked cases
    positive_cases = [p for p, s in tracer.covid_status.items() if s["status"] == "positive"]
    if positive_cases:
        st.info(f"**Current COVID+ Cases ({len(positive_cases)}):** {', '.join(positive_cases)}")
        
        # Cluster analysis for positive cases
        with st.expander("🔍 View Cluster Analysis", expanded=True):
            clusters, labels = tracer.get_cluster_info(contact_radius, min_samples)
            
            st.write(f"**Settings:** Contact Radius = {contact_radius}m, Min Samples = {min_samples}")
            st.write(f"**Total Clusters Found:** {len([c for c in clusters.keys() if c != -1])}")
            st.write(f"**Noise Points (no cluster):** {len(clusters.get(-1, []))}")
            
            # Find which clusters contain positive cases
            for cluster_id, people in clusters.items():
                if cluster_id == -1:
                    continue
                    
                positive_in_cluster = [p for p in people if p in positive_cases]
                if positive_in_cluster:
                    st.warning(
                        f"**Cluster {cluster_id}:** {len(people)} people, "
                        f"{len(positive_in_cluster)} COVID+ ({', '.join(positive_in_cluster)})"
                    )
                    # Show some contacts
                    contacts = [p for p in people if p not in positive_cases][:5]
                    if contacts:
                        st.write(f"  → Contacts: {', '.join(contacts)}" + 
                               (" ..." if len(people) - len(positive_in_cluster) > 5 else ""))
            
            # Show if any positive cases are isolated (in noise)
            isolated = [p for p in positive_cases if p in clusters.get(-1, [])]
            if isolated:
                st.error(f"⚠️ **Isolated (No Contacts Found):** {', '.join(isolated)}")
                st.caption("These people are not in any cluster. Try increasing Contact Radius.")

    stats = tracer.get_dashboard_stats()
    cols = st.columns(5)
    for c, (k, v) in zip(cols, stats.items()):
        c.metric(k.replace("_", " ").title(), v)

    risk_df = pd.DataFrame.from_dict(
        tracer.covid_status, orient="index"
    ).reset_index(names="person")

    fig = px.bar(
        risk_df.sort_values("risk_score", ascending=False).head(20),
        x="risk_score",
        y="person",
        color="status",
        orientation="h",
        title="Top 20 At-Risk Individuals",
    )
    st.plotly_chart(fig, use_container_width=True)

    colors = [
        "red" if tracer.covid_status[d["id"]]["status"] == "positive"
        else "orange" if tracer.covid_status[d["id"]]["status"] == "high_risk"
        else "yellow" if tracer.covid_status[d["id"]]["status"] == "low_risk"
        else "green"
        for d in tracer.data
    ]

    fig_map = go.Figure(go.Scattermapbox(
        lat=tracer.coords[:, 0],
        lon=tracer.coords[:, 1],
        mode="markers",
        marker=dict(size=6, color=colors),
        text=[
            f"{d['id']} — {tracer.covid_status[d['id']]['status']}"
            for d in tracer.data
        ],
    ))

    fig_map.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(center=dict(lat=17.3850, lon=78.4867), zoom=10),
        title="Hyderabad Contact Risk Map",
    )

    st.plotly_chart(fig_map, use_container_width=True)


# ===================== CLI =====================

def main_cli():
    tracer = AdvancedContactTracing("data.json")
    tracer.mark_covid_case("Rajesh Kumar")
    tracer.calculate_risk_propagation()
    tracer.save_status()
    print(tracer.get_dashboard_stats())


if __name__ == "__main__":
    import sys
    # When using streamlit run, sys.argv doesn't work as expected
    # Always run the dashboard when executed with streamlit
    run_dashboard()
