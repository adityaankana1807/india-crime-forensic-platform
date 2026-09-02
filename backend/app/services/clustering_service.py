import pandas as pd
from sklearn.cluster import DBSCAN

from app.config import DATA_SYNTHETIC_DIR

HOTSPOTS_PATH = DATA_SYNTHETIC_DIR / "crime_hotspots.csv"


def detect_hotspots(eps_km: float = 5.0, min_samples: int = 10) -> dict:
    df = pd.read_csv(HOTSPOTS_PATH)
    coords = df[["latitude", "longitude"]].to_numpy()

    # approximate degrees-per-km at mid latitudes for a simple haversine-free radius
    eps_deg = eps_km / 111.0
    labels = DBSCAN(eps=eps_deg, min_samples=min_samples).fit_predict(coords)
    df["cluster"] = labels

    clusters = []
    for cluster_id, group in df[df["cluster"] != -1].groupby("cluster"):
        clusters.append({
            "cluster_id": int(cluster_id),
            "size": int(len(group)),
            "center_lat": round(float(group["latitude"].mean()), 5),
            "center_lon": round(float(group["longitude"].mean()), 5),
            "dominant_city": group["city"].mode().iat[0],
            "dominant_crime_type": group["crime_type"].mode().iat[0],
            "high_threat_share": round(
                float((group["threat_level"].isin(["high", "critical"])).mean()), 3
            ),
        })
    clusters.sort(key=lambda c: c["size"], reverse=True)

    noise_count = int((labels == -1).sum())
    return {
        "total_points": len(df),
        "cluster_count": len(clusters),
        "noise_points": noise_count,
        "clusters": clusters,
    }


def crime_trends() -> dict:
    df = pd.read_csv(HOTSPOTS_PATH, parse_dates=["date"])
    by_type = df["crime_type"].value_counts().to_dict()
    by_threat = df["threat_level"].value_counts().to_dict()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    by_month = df.groupby("month").size().to_dict()
    by_city = df["city"].value_counts().to_dict()
    return {
        "by_crime_type": by_type,
        "by_threat_level": by_threat,
        "by_month": dict(sorted(by_month.items())),
        "by_city": by_city,
    }
