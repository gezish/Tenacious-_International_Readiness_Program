> Hi, I’m Gezahegne. For Week 3 of the International Readiness Program, I worked on the **backend** feature of the Engagement Module.

### 🏗️ What I Built
- A FastAPI-based REST API that provides engagement analytics data.
- The `/engagement` endpoint supports filters (`user_type`, `from_date`, `to_date`) and returns both a `summary` and a detailed log.

### 📦 CSV Support
- I added a `/engagement/import` endpoint where admins can upload a `.csv` file containing logs.
- I also built a `/engagement/export` endpoint to download filtered data as a `.csv`.

### 📊 Summary
- The system dynamically calculates total actions, number of active users, and an average session time estimate.
- The backend is structured to support frontend dashboards via JSON and CSV.

> Thanks for watching! Code is available on GitHub and ready for integration.