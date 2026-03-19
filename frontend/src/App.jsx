import { useState } from "react"
import Dashboard from "./components/Dashboard"
import Predict from "./components/Predict"
import "./App.css"

export default function App() {
  const [page, setPage] = useState("dashboard")
  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-brand">
          <div className="nav-logo">⚡</div>
          <div>
            <div className="nav-title">EnergyInsight</div>
            <div className="nav-tagline">Household Power Analytics</div>
          </div>
        </div>
        <div className="nav-links">
          <button className={page === "dashboard" ? "nav-btn active" : "nav-btn"} onClick={() => setPage("dashboard")}>
            Dashboard
          </button>
          <button className={page === "predict" ? "nav-btn active" : "nav-btn"} onClick={() => setPage("predict")}>
            Predict & Cost
          </button>
        </div>
      </nav>
      <main className="main-content">
        {page === "dashboard" ? <Dashboard /> : <Predict />}
      </main>
    </div>
  )
}