# FMHY Web Viewer

A modern, minimalistic web application to explore and search the [FMHY (FreeMediaHeckYeah)](https://fmhy.net/) dataset.

![Modern UI](https://img.shields.io/badge/UI-Minimalist-black?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Frontend-Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)

## ✨ Features

- **Modern & Minimalist Design:** Clean UI built with Tailwind CSS and Lucide icons.
- **Fast Search:** Instant search across the entire FMHY collection (10MB+ JSON).
- **Responsive Layout:** Works seamlessly on desktop and mobile devices.
- **Dark Mode Support:** Adapts to your system's color scheme.
- **Category Navigation:** Browse through categorized sections easily via the sidebar.

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **npm** (or yarn/pnpm)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/minhduc1212/TheLastFortress.git
   cd TheLastFortress
   ```

2. **Setup Backend (FastAPI):**
   ```bash
   # Create a virtual environment (optional but recommended)
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install fastapi uvicorn
   ```

3. **Setup Frontend (Next.js):**
   ```bash
   cd frontend
   npm install
   ```

## 🛠️ How to Run

You need to run both the backend and the frontend simultaneously.

### 1. Start the Backend
From the project root:
```bash
cd backend
uvicorn app:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

### 2. Start the Frontend
From the project root in a new terminal:
```bash
cd frontend
npm run dev
```
The application will be available at `http://localhost:3000`.

## 📖 Usage

1.  **Browse:** Use the sidebar on the left to navigate through different FMHY categories (Beginners Guide, Movies, etc.).
2.  **Search:** Use the top search bar to find specific sites, tools, or guides. The search covers headings, descriptions, and URLs.
3.  **Explore:** Click on the resource buttons to open the links in a new tab.
4.  **Responsive:** On mobile, use the menu icon to toggle the category sidebar.

## 📂 Project Structure

- `backend/`: FastAPI application logic and data serving.
- `frontend/`: Next.js source code, components, and styles.
- `fmhy_all_data.json`: The source dataset.
- `main.py`: The original crawler script used to generate the data.

## 📝 License

This project is open-source. Feel free to use and modify it.
