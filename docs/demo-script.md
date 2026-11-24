# One-to-Two Minute Demo Script

Approximate total duration: 1 minute 40 seconds.

## 0:00-0:15 - Introduction

"This project is a Student Query Chatbot built as a recruiter-facing portfolio
project. It lets a student enter a question and receive a predefined response
for topics such as admissions, fees, examinations, and campus facilities."

## 0:15-0:30 - Problem and interface

"Students often search several pages for common questions. This prototype
demonstrates a simple web interface that classifies a query and routes it to a
dataset-backed answer. The college data shown here is sample placeholder
content, not verified institutional information."

Show the main interface and the suggested-question buttons.

## 0:30-0:45 - Successful query

Ask: "What is the admission process?"

"The React frontend sends this question to FastAPI. The backend preprocesses
it, creates character n-gram TF-IDF features, and uses Logistic Regression to
predict an intent. The response service then looks up a response in the JSON
dataset."

## 0:45-1:00 - Architecture

Briefly show the system-architecture diagram or the README architecture
section.

"The stack is React and Vite on the frontend, FastAPI and Uvicorn on the
backend, scikit-learn for NLP, and Joblib for the saved model artifacts."

## 1:00-1:15 - Fallback

Ask: "xylophonic quasar blorptastic"

"If the query has no useful features or low classifier confidence, the response
service uses a safe fallback. This project does not use a generative AI model."

## 1:15-1:30 - Health and results

Open `/health` in a browser tab.

"The health route confirms that the web process is responding. The project also
has evaluation outputs and tests. Its current fixed holdout has 22 examples,
and the metrics should be viewed as evidence of this small synthetic dataset's
behavior, not as a production accuracy claim."

## 1:30-1:40 - Closing

"The project includes dataset validation, backend and frontend tests, deployment
configuration, and complete setup documentation. The next work is to replace
placeholder data and evaluate against a larger, reviewed set of real student
queries."
