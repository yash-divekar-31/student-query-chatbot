# Demo Storyboard

| Scene | Duration | Screen | Action | Narration |
| --- | --- | --- | --- | --- |
| 1. Introduction | 10 sec | Main chatbot interface | Reset chat and show the welcome state | Introduce the project and its purpose |
| 2. Problem and sample notice | 10 sec | README or interface | Show the sample-data notice | Explain the prototype problem statement and placeholder-data limitation |
| 3. Suggested questions | 10 sec | Interface | Hover or select a suggested question | Show the responsive UI and available example queries |
| 4. Successful response | 15 sec | Interface with `What is the admission process?` conversation | Submit the query and allow the response to appear | Explain React-to-FastAPI request and dataset response lookup |
| 5. Architecture | 15 sec | README architecture section or system diagram | Point through browser, API, classifier, and JSON dataset | Explain the React/FastAPI/scikit-learn stack |
| 6. Fallback | 15 sec | Interface with unknown query | Submit `xylophonic quasar blorptastic` | Explain low-confidence fallback and that no LLM is used |
| 7. Health endpoint | 10 sec | Browser tab at `/health` | Show the JSON status response | Explain basic process health; `/chat` is the model/service readiness check |
| 8. Evaluation and closing | 15 sec | NLP pipeline or evaluation files | Show metric summary and confusion-matrix image | Report the measured holdout honestly and identify the remaining validation work |

## Recording instructions

1. Start the FastAPI and Vite servers.
2. Verify the application and `/health` before recording.
3. Use a 1280x720 or 1920x1080 browser window.
4. Clear chat before the intro and suggested-question scenes.
5. Keep the cursor visible but avoid rapid movement.
6. Use only sample queries and placeholder content.
7. Export as MP4 or WebM and save it under `docs/demo/` if created.
