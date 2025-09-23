import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import MagicMock, patch
from app import calculate_scores

def test_calculate_scores_all_neutral():
    """
    Tests that when the user answers "Neutral" (3) to all questions,
    the score for all categories should be 3.0.
    """
    # Create mock form data as if all 48 questions are answered with 3 (q0 to q47).
    mock_form_data = {f"q{i}": "3" for i in range(48)}
    
    # Calculate scores
    scores = calculate_scores(mock_form_data)
    
    # Expected result: Average should be 3.0 for each category
    expected_scores = {
        'R': 3.0, 'I': 3.0, 'A': 3.0,
        'S': 3.0, 'E': 3.0, 'C': 3.0
    }
    
    # Check if the result is as expected
    assert scores == expected_scores

def test_calculate_scores_max_realistic():
    """
    Tests that when the user answers "Like Very Much" (5) to all Realistic questions,
    and "Dislike Very Much" (1) to all other questions,
    the Realistic score should be 5.0 and others should be 1.0.
    """
    mock_form_data = {}
    # Give 5 to Realistic questions (first 8 questions, q0-q7)
    for i in range(8):
        mock_form_data[f"q{i}"] = "5"
    
    # Give 1 to all other questions (q8-q47)
    for i in range(8, 48):
        mock_form_data[f"q{i}"] = "1"

    scores = calculate_scores(mock_form_data)

    expected_scores = {
        'R': 5.0, 'I': 1.0, 'A': 1.0,
        'S': 1.0, 'E': 1.0, 'C': 1.0
    }

    assert scores == expected_scores


def test_home_page(client):
    """
    Tests whether the home page (/) loads successfully.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Career Interest Survey" in response.data # Check if the page title exists in the HTML

def test_recommend_endpoint_basic(client):
    """
    Tests whether a basic request to the /recommend endpoint is successful.
    This test does not check the database or AI part yet, it only verifies if the endpoint works.
    """
    # Send data as if all answers are "Neutral"
    mock_form_data = {f"q{i}": "3" for i in range(48)}

    response = client.post('/recommend', json=mock_form_data)
    
    assert response.status_code == 200
    assert response.is_json
    
    json_data = response.get_json()
    
    # Check for actual keys
    assert 'recommendations' in json_data
    assert 'chart_images' in json_data


def test_chat_endpoint_with_code(client):
    """
    Tests the original /chat function by mocking both LLM and database calls.
    """
    # Prepare fake API and Database responses
    mock_llm_response_content = "This is the final AI answer."
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message = MagicMock()
    mock_llm_response.choices[0].message.content = mock_llm_response_content

    mock_db_results = {
        "documents": [
            ["Doc 1: Info about marketing.", "Doc 2: Info about sales."]
        ]
    }

    # Set up patches (objects to be mocked)
    with patch('app.llm_client') as mock_llm, \
         patch('app.onet_collection') as mock_db:

        # Set what the fake objects' methods should return
        mock_llm.chat.completions.create.return_value = mock_llm_response
        mock_db.query.return_value = mock_db_results

        # Send request with correct JSON data as expected by the original code
        response = client.post('/chat', json={
            'question': 'Tell me about marketing jobs.',
            'profile_summary': 'R:4.5, I:3.2, A:2.1, S:4.8, E:3.9, C:4.1'
        })

        # Validate results
        response_data = response.get_json()

        # Check status code and error message
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Data: {response_data}"

        # Check if the returned answer is correct
        assert 'answer' in response_data
        assert response_data['answer'] == mock_llm_response_content

        # Check that the mocked functions were called correctly
        mock_db.query.assert_called_once_with(
            query_texts=['Tell me about marketing jobs.'],
            n_results=5
        )
        mock_llm.chat.completions.create.assert_called_once()
