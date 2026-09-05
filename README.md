# AI Interview Simulator

A local Streamlit app for practising job interviews. Upload a PDF resume, answer AI-generated questions across aptitude, technical, coding, and HR rounds, and receive AI scoring, feedback, optional camera-based emotion analysis, and stored results.

## Features

- PDF resume text extraction with personalized question generation
- Four interview rounds: aptitude, technical, coding, and HR
- Microphone transcription for spoken answers and a text editor for coding answers
- Optional camera snapshots for emotion analysis
- AI evaluation with per-question feedback and an overall score
- SQLite-backed interview history and personal performance statistics
- Guest sessions, employee sessions, and interviewer scheduling/results dashboard
- Optional Gmail notifications for scheduled interviews and completed results

## Tech stack

- Python and Streamlit
- OpenAI Python SDK for question generation and answer evaluation
- SQLite for local persistence
- pdfplumber for PDF parsing
- SpeechRecognition and PyAudio for microphone input
- OpenCV, DeepFace, NumPy, and Pillow for camera/emotion analysis
- Gmail SMTP for optional email notifications

## Prerequisites

- Python 3.10 or newer (the project is currently tested with Python 3.13)
- `pip` and a working microphone for spoken-answer capture
- An OpenAI API key with access to the configured chat-completions model
- Optional: a Gmail account with two-factor authentication and an app password for notifications
- Optional: a webcam for emotion analysis

On Windows, PyAudio may require the Microsoft C++ Build Tools if pip cannot find a compatible wheel. Install the build tools, then rerun the dependency command.

## Setup

From a fresh clone, open a terminal in the project root and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set at least:

```dotenv
OPENAI_API_KEY=your_openai_api_key
```

Email is optional. To enable notifications, also set `SENDER_EMAIL` and `SENDER_PASSWORD` to a Gmail address and a Gmail app password. `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are reserved for a future OAuth integration and are not required by the current login flow.

## Run the app

Initialize the database and start Streamlit:

```powershell
python init_db.py
streamlit run app.py
```

Then open the URL printed by Streamlit, normally `http://localhost:8501`.

On Windows, the included launchers perform the same setup after a virtual environment has been created:

```powershell
.\start.ps1
```

or:

```bat
start.bat
```

## Project structure

```text
.
├── app.py                    # Landing page, session login, employee/interviewer dashboards
├── pages/
│   ├── 1_Interview.py        # Resume upload, questions, recording, coding responses, camera input
│   ├── 2_Results.py          # AI evaluation, scores, saving, and result emails
│   └── 3_Admin.py            # Interviewer scheduling and results management
├── modules/
│   ├── auth.py               # Streamlit session helpers and OAuth utility functions
│   ├── database.py           # SQLite schema and data access
│   ├── resume_parser.py      # PDF text extraction
│   ├── question_gen.py       # OpenAI question generation
│   ├── evaluator.py          # OpenAI answer evaluation
│   ├── speech_to_text.py     # Microphone recording and Google transcription
│   ├── emotion_detect.py     # DeepFace emotion analysis
│   └── email_service.py      # Gmail SMTP notifications
├── .streamlit/config.toml    # Streamlit server and theme configuration
├── .env.example              # Environment-variable template
├── init_db.py                # Database initializer
├── requirements.txt          # Python dependencies
├── start.ps1 / start.bat     # Windows launch helpers
└── interview_results.db      # Local SQLite database (created automatically)
```

## How to use it

1. On the landing page, choose **Start as Guest** for an unsaved practice session, or **Continue with Google** and enter a Gmail/Google Workspace address. The current implementation uses this email form rather than a real Google OAuth redirect.
2. Select **Employee** to practise interviews. Select **Interviewer** to schedule employee interviews and view their results.
3. As an employee, select **Start Practice Interview**, upload a text-based PDF resume, and wait for questions to be generated.
4. Work through every question. Use the microphone for aptitude, technical, and HR answers; use the coding editor for coding questions. You can skip a question. Camera input is optional.
5. After all questions in a round are answered or skipped, continue to the next round. At the end, select **View Results**.
6. Review scores and feedback. Logged-in, non-guest users have their results stored in `interview_results.db`; email is sent only when Gmail settings are configured.

## Troubleshooting

- **`OPENAI_API_KEY` error or question generation fails:** ensure `.env` exists in the project root, contains a valid key, and restart Streamlit after editing it.
- **Microphone unavailable:** confirm that Windows has granted microphone permission to the terminal/Python and that PyAudio installed successfully. The app needs internet access for Google speech recognition.
- **No text from a PDF:** use a text-based PDF; scanned image-only resumes may not contain extractable text.
- **Email warnings:** email delivery is optional. Check the Gmail address and app password; normal Gmail passwords will not work.
- **Database problems during development:** close any running app instances, then remove only `interview_results.db` if you intentionally want to discard local interview history. Restarting the app recreates the schema.
- **DeepFace/model download delay:** the first camera analysis can take longer because DeepFace may download model files.

## Known limitations

- “Google login” is currently an email-based development login, not authenticated Google OAuth.
- The application is designed for local development and stores data in a local SQLite file; it is not a multi-user production deployment.
- AI results and speech transcription require external services and network access.
