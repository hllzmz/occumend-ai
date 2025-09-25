from flask import Blueprint, render_template, request, jsonify, current_app
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from .visualizations import create_radar_chart_image, create_bar_chart_image
from .services import get_ai_response

bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/recommend", methods=["POST"])
def recommend():
    df_clustered_jobs = current_app.df_clustered_jobs
    if df_clustered_jobs is None:
        return jsonify({"error": "Server could not load data. Please check the logs."}), 500

    user_answers = request.json
    user_profile = {
        "R_score": np.mean(user_answers.get("R", [0])), "I_score": np.mean(user_answers.get("I", [0])),
        "A_score": np.mean(user_answers.get("A", [0])), "S_score": np.mean(user_answers.get("S", [0])),
        "E_score": np.mean(user_answers.get("E", [0])), "C_score": np.mean(user_answers.get("C", [0])),
    }

    features = ["R_score", "I_score", "A_score", "S_score", "E_score", "C_score"]
    job_scores = df_clustered_jobs[features].fillna(0)
    user_vector = pd.DataFrame([user_profile])[features].values
    
    similarity_scores = cosine_similarity(user_vector, job_scores.values)
    df_clustered_jobs["similarity"] = similarity_scores[0]

    top_jobs = df_clustered_jobs.sort_values(by="similarity", ascending=False).head(20)

    recommendations = []
    for index, row in top_jobs.iterrows():
        recommendations.append({
            "Title": row["Title"], "cluster_name": row["cluster_name"], "similarity": row["similarity"],
            "knowledge": current_app.knowledge_map.get(index, []),
            "skills": current_app.skills_map.get(index, []),
            "abilities": current_app.abilities_map.get(index, []),
        })

    radar_chart_img = create_radar_chart_image(list(user_profile.values()))
    bar_chart_img = create_bar_chart_image(recommendations)

    return jsonify({
        "recommendations": recommendations,
        "chart_images": {"radar": radar_chart_img, "bar": bar_chart_img},
    })

@bp.route("/chat", methods=["POST"])
def chat():
    if not current_app.llm_client:
        return jsonify({"error": "LLM client is not configured on the server."}), 500
    if not current_app.onet_collection:
        return jsonify({"error": "ONET collection is not configured on the server."}), 500

    data = request.json
    user_question = data.get("question")
    profile_summary = data.get("profile_summary")

    if not user_question or not profile_summary:
        return jsonify({"error": "Question and profile summary are required."}), 400

    try:
        answer = get_ai_response(
            llm_client=current_app.llm_client,
            onet_collection=current_app.onet_collection,
            user_question=user_question,
            profile_summary=profile_summary,
            model=current_app.config['LLM_CHAT_MODEL'],
            embedding_model=current_app.embedding_model,
        )
        return jsonify({"answer": answer})
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error occurred in /chat: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500