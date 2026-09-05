# modules/evaluator.py
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_answer(question, answer, round_type="technical"):
    """
    Evaluate interview answer and provide scores based on round type.
    
    Args:
        question: The question asked
        answer: The candidate's answer
        round_type: "aptitude", "technical", "coding", or "hr"
    
    Returns:
        JSON string with scores and feedback
    """
    
    round_criteria = {
        "aptitude": """
        Evaluate on:
        1. Logical Correctness (0-10): Is the reasoning sound and logical?
        2. Problem-Solving Approach (0-10): Is the methodology clear and structured?
        3. Clarity of Explanation (0-10): How well explained is the solution?
        """,
        
        "technical": """
        Evaluate on:
        1. Technical Accuracy (0-10): Are the technical details correct?
        2. Depth of Knowledge (0-10): Does the answer show deep understanding?
        3. Communication (0-10): How clearly is the answer presented?
        """,
        
        "coding": """
        Evaluate on:
        1. Solution Correctness (0-10): Does the code/approach solve the problem?
        2. Code Quality (0-10): Is the code efficient and well-structured?
        3. Explanation (0-10): Can they explain the algorithm clearly?
        """,
        
        "hr": """
        Evaluate on:
        1. Authenticity (0-10): Does the answer seem genuine and thoughtful?
        2. Communication Skills (0-10): Is the answer clear and well-articulated?
        3. Soft Skills Assessment (0-10): Does it demonstrate leadership, teamwork, etc?
        """
    }
    
    criteria = round_criteria.get(round_type, round_criteria["technical"])
    
    prompt = f"""
    Evaluate this {round_type.upper()} ROUND interview answer and give scores.
    
    Question: {question}
    Answer: {answer}
    
    {criteria}
    
    Also provide:
    - Key Strengths: 2-3 points (brief)
    - Areas for Improvement: 2-3 points (brief)
    
    Format your response as JSON with keys: score1, score1_name, score2, score2_name, score3, score3_name, 
    strengths (array), improvements (array), overall_feedback
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
