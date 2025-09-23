import pandas as pd
from sklearn.cluster import KMeans


def load_and_prepare_data(config):
    """Loads data files from Parquet, merges them, and performs clustering."""
    try:
        # Load and Merge Data using faster Parquet format
        df_jobs = pd.read_parquet(
            config["OCCUPATIONS_FILE_PATH"], columns=["O*NET-SOC Code", "Title"]
        ).set_index("O*NET-SOC Code")

        df_interests = pd.read_parquet(config["INTERESTS_FILE_PATH"])
        df_interests = df_interests[df_interests["Scale ID"] == "OI"]

        df_riasec_profiles = df_interests.pivot_table(
            index="O*NET-SOC Code", columns="Element ID", values="Data Value"
        )

        riasec_mapping = {
            "1.B.1.a": "R_score",
            "1.B.1.b": "I_score",
            "1.B.1.c": "A_score",
            "1.B.1.d": "S_score",
            "1.B.1.e": "E_score",
            "1.B.1.f": "C_score",
        }
        df_riasec_profiles.rename(columns=riasec_mapping, inplace=True)
        df_job_profiles = df_jobs.join(df_riasec_profiles, how="inner")

        # Clustering
        features = ["R_score", "I_score", "A_score", "S_score", "E_score", "C_score"]
        job_scores = df_job_profiles[features].fillna(0)
        kmeans = KMeans(
            n_clusters=8, random_state=42, n_init="auto"
        ) 
        df_job_profiles["cluster"] = kmeans.fit_predict(job_scores)
        cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=features)

        def get_cluster_name(center):
            top_three = center.nlargest(3).index
            return f"{top_three[0][0]}-{top_three[1][0]}-{top_three[2][0]}"

        cluster_centers["cluster_name"] = cluster_centers.apply(
            get_cluster_name, axis=1
        )
        df_job_profiles["cluster_name"] = df_job_profiles["cluster"].map(
            cluster_centers["cluster_name"].to_dict()
        )

        # Create knowledge, skills and abilities maps
        knowledge_map = _get_top_elements(config["KNOWLEDGE_FILE_PATH"])
        skills_map = _get_top_elements(config["SKILLS_FILE_PATH"])
        abilities_map = _get_top_elements(config["ABILITIES_FILE_PATH"])

        print("Data loaded and prepared successfully from Parquet files.")
        return df_job_profiles, knowledge_map, skills_map, abilities_map

    except FileNotFoundError as e:
        print(f"ERROR: Required data file not found: '{e.filename}'.")
        print(
            "Please ensure you have run 'python convert_data.py' locally and committed the .parquet files."
        )
        return None, None, None, None
    except Exception as e:
        print(f"An unexpected error occurred during data processing: {e}")
        return None, None, None, None


def _get_top_elements(filename, scale_id_filter="IM"):
    """Helper function: Gets the top 5 elements for each occupation from Parquet files."""
    try:
        df = pd.read_parquet(filename)
        df_important = df[df["Scale ID"] == scale_id_filter]
        top_elements = (
            df_important.sort_values("Data Value", ascending=False)
            .groupby("O*NET-SOC Code")
            .head(5)
        )
        return (
            top_elements.groupby("O*NET-SOC Code")["Element Name"].apply(list).to_dict()
        )
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print(
            f"Warning: Competency file not found or is empty: '{filename}'. This section will be skipped."
        )
        return {}
