# modules/question_gen.py
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_questions(resume_text, round_type="technical", num_questions=3):
    """
    Generate interview questions based on round type.
    
    Args:
        resume_text: Extracted text from resume
        round_type: "aptitude", "technical", "coding", or "hr"
        num_questions: Number of questions to generate
    
    Returns:
        String with numbered questions, one per line
    """
    

    round_prompts = {
        "aptitude": f"""
        Generate {num_questions} MATHEMATICAL APTITUDE questions covering real quantitative reasoning topics.
        
        Focus on these types of questions:
        - Number series and patterns (e.g., 2, 4, 8, 16, ?)
        - Simple percentage calculations (e.g., 20% of 500)
        - Ratio and proportion problems
        - Simple interest and profit-loss calculations
        - Speed, distance, and time problems
        - Basic probability questions
        - Number system basics (odd, even, prime numbers)
        
        Keep questions BEGINNER to INTERMEDIATE level - simple enough for freshers but test basic math skills.
        Include numerical values or simple word problems.
        Do NOT include logic puzzles or reasoning about hypothetical scenarios.
        
        Ignore the resume content for this round.
        Return only the questions as a numbered list (no solutions or explanations).
        """,
        "technical": f"""
        Based on this resume, generate {num_questions} BASIC TECHNICAL questions.
        Focus on fundamental concepts and simple technology questions.
        Ask easy questions about their technical background - avoid advanced topics.
        Questions should be beginner-friendly and straightforward.
        
        Resume:
        {resume_text}
        
        Return only the questions as a numbered list (no explanations).
        """,
        "coding": f"""
        Based on this resume, generate {num_questions} BEGINNER-LEVEL programming challenges for a coding round.
        
        Look at the candidate's programming languages, frameworks, and projects from their resume and tailor
        the problems to their background. For example:
        - If they know Python, ask a Python-relevant problem (e.g., list manipulation, string processing)
        - If they know JavaScript/web, ask about DOM logic or array operations
        - If they have database experience, ask a simple query or data-filtering problem
        - If they list any projects, base a problem around a concept from that domain
        
        Keep problems BEGINNER to INTERMEDIATE level — no complex algorithms or advanced data structures.
        Problems should be short and completable in a few minutes.
        
        IMPORTANT: Ask candidates to specify which programming language they will use (Python, JavaScript, Java, C++, etc.)
        
        Resume:
        {resume_text}
        
        Return only the coding problems as a numbered list (no solutions or explanations).
        """,
        "hr": f"""
        Based on this resume, generate {num_questions} SIMPLE HR/BEHAVIORAL questions.
        Focus on personality, communication, and basic teamwork skills.
        Ask easy, straightforward questions suitable for beginners.
        Avoid complex scenarios - keep questions simple and direct.
        
        Resume:
        {resume_text}
        
        Return only the questions as a numbered list (no explanations).
        """
    }

    prompt = round_prompts.get(round_type, round_prompts["technical"])
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content