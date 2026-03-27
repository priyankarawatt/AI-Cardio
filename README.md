AI Cardio 🫀 
**An AI-powered web dashboard that predicts heart disease risk and provides personalized, real-time health recommendations.**

Project Overview
AI Cardio is a full-stack web application designed to help users monitor their heart health. By inputting basic health metrics (like blood pressure, cholesterol, age, and lifestyle habits), the system uses a trained Machine Learning model to assess the user's risk of heart disease. It features an interactive dashboard, historical data tracking, and a built-in AI Heart Assistant to explain results and offer actionable health advice.

---

👨‍💻 My Contributions (Lead Frontend & UI/UX Developer)
I took ownership of the user interface, frontend logic, and overall user experience. My goal was to take the complex data outputted by the Machine Learning model and present it in a clean, modern, and highly interactive way.

**Key Features I Built:**
* **Dynamic Dashboard:** Engineered a responsive, single-page dashboard layout using HTML5, CSS3, and JavaScript Flexbox/Grid.
* **Premium UI/UX Design:** Implemented modern web design trends including "Glassmorphism" (frosted glass effects), custom CSS animations (like the heartbeat EKG line), and custom scrollbars for a polished, app-like feel.
* **Data Visualization:** Integrated **Chart.js** to dynamically render the user's risk factors into an interactive pie chart based on their real-time SQLite database records.
* **AI Chatbot Interface:** Built the frontend architecture for the "AI Heart Doctor." I designed the chat UI, implemented the smooth-scrolling logic, and created dynamic "Quick Suggestion" chips that rotate using JavaScript intervals to guide the user.
* **Frontend-to-Backend Integration:** Wrote the asynchronous JavaScript (`fetch` API) to seamlessly connect the frontend chat interface to the Python/Flask backend without requiring page reloads.

---

🤝 Collaborative Work & Machine Learning
This project was built collaboratively. While I spearheaded the frontend architecture and user experience, my teammate focused on the pages like home, history and graps etc:
* **Machine Learning:** Trained and exported the predictive model (`heart_model.pkl`) using scikit-learn.
* **Backend Routing:** Assisted in setting up the initial Flask routing and SQLite database architecture to handle user authentication and store assessment history.

---

🛠️ Tech Stack
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Chart.js, Lucide Icons
* **Backend:** Python, Flask, SQLite3
* **Machine Learning:** Scikit-learn, Pandas, Joblib
