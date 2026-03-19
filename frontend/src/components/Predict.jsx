import { useState, useEffect } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8000"

const defaults = {
  hour: 12, day_of_week: 1, month: 6, is_weekend: 0,
  rolling_mean_1h: 1.2, rolling_mean_24h: 1.1,
  lag_1h: 1.15, lag_24h: 1.05,
  Voltage: 240.0, Global_intensity: 5.0,
  Sub_metering_1: 0.0, Sub_metering_2: 1.0, Sub_metering_3: 17.0,
}

function getInterpretation(val) {
  if (val < 0.5) return { text: "Very low consumption. Minimal appliances in use — standby or sleep mode.", level: "normal" }
  if (val < 1.0) return { text: "Low consumption. Typical off-peak period. Lights and basic appliances only.", level: "normal" }
  if (val < 2.0) return { text: "Moderate consumption. Normal household activity — TV, fridge, lighting.", level: "normal" }
  if (val < 3.5) return { text: "High consumption. Multiple appliances running — AC, washing machine, oven.", level: "warn" }
  return { text: "Very high consumption. Peak usage — consider switching off non-essential appliances.", level: "danger" }
}

export default function Predict() {
  const [form,    setForm]    = useState(defaults)
  const [state,   setState]   = useState("Telangana")
  const [states,  setStates]  = useState([])
  const [result,  setResult]  = useState(null)
  const [hours,   setHours]   = useState(24)
  const [days,    setDays]    = useState(30)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    axios.get(`${API}/states`)
      .then(r => setStates(r.data.states))
      .catch(() => {})
  }, [])

  const handleChange = e => setForm({ ...form, [e.target.name]: parseFloat(e.target.value) })

  const handleSubmit = async () => {
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await axios.post(`${API}/predict`, { ...form, state })
      setResult(res.data)
    } catch {
      setError("Prediction failed. Make sure FastAPI is running on port 8000.")
    } finally {
      setLoading(false)
    }
  }

  const totalUnits = result ? (result.predicted_power_kw * hours * days).toFixed(2) : null
  const interp     = result ? getInterpretation(result.predicted_power_kw) : null
  const selectedState = states.find(s => s.name === state)

  return (
    <div>
      <div className="page-header">
        <p className="page-title">Predict & Cost Estimator</p>
        <p className="page-sub">Enter household conditions and select your state to get power prediction and electricity bill estimate.</p>
      </div>

      <div className="predict-grid">
        <div className="predict-form">

          <div className="form-section">State / electricity board</div>
          <div style={{ marginBottom: 14 }}>
            <div className="form-group">
              <label>Select your state</label>
              <select
                value={state}
                onChange={e => { setState(e.target.value); setResult(null) }}
                style={{
                  padding: "9px 12px",
                  border: "1px solid var(--border2)",
                  borderRadius: 8,
                  fontSize: 14,
                  color: "var(--navy)",
                  background: "var(--surface2)",
                  outline: "none",
                  cursor: "pointer",
                  width: "100%",
                }}
              >
                {states.map(s => (
                  <option key={s.name} value={s.name}>{s.name}</option>
                ))}
              </select>
            </div>
            {selectedState && (
              <div style={{
                marginTop: 8, padding: "7px 12px",
                background: "#f0fdf4", borderRadius: 8,
                fontSize: 12, color: "#15803d",
                border: "1px solid #bbf7d0",
                display: "flex", justifyContent: "space-between"
              }}>
                <span>Electricity Board</span>
                <strong>{selectedState.board}</strong>
              </div>
            )}
          </div>

          <div className="form-section">Time features</div>
          <div className="form-row">
            <div className="form-group">
              <label>Hour (0–23)</label>
              <input type="number" name="hour" min="0" max="23" value={form.hour} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Day of week (0=Mon)</label>
              <input type="number" name="day_of_week" min="0" max="6" value={form.day_of_week} onChange={handleChange} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Month (1–12)</label>
              <input type="number" name="month" min="1" max="12" value={form.month} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Is weekend (0/1)</label>
              <input type="number" name="is_weekend" min="0" max="1" value={form.is_weekend} onChange={handleChange} />
            </div>
          </div>

          <div className="form-section">Rolling & lag features</div>
          <div className="form-row">
            <div className="form-group">
              <label>Rolling mean 1h (kW)</label>
              <input type="number" step="0.01" name="rolling_mean_1h" value={form.rolling_mean_1h} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Rolling mean 24h (kW)</label>
              <input type="number" step="0.01" name="rolling_mean_24h" value={form.rolling_mean_24h} onChange={handleChange} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Lag 1h (kW)</label>
              <input type="number" step="0.01" name="lag_1h" value={form.lag_1h} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Lag 24h (kW)</label>
              <input type="number" step="0.01" name="lag_24h" value={form.lag_24h} onChange={handleChange} />
            </div>
          </div>

          <div className="form-section">Electrical readings</div>
          <div className="form-row">
            <div className="form-group">
              <label>Voltage (V)</label>
              <input type="number" step="0.1" name="Voltage" value={form.Voltage} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Global intensity (A)</label>
              <input type="number" step="0.1" name="Global_intensity" value={form.Global_intensity} onChange={handleChange} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Sub metering 1 (Wh)</label>
              <input type="number" step="0.1" name="Sub_metering_1" value={form.Sub_metering_1} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Sub metering 2 (Wh)</label>
              <input type="number" step="0.1" name="Sub_metering_2" value={form.Sub_metering_2} onChange={handleChange} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Sub metering 3 (Wh)</label>
              <input type="number" step="0.1" name="Sub_metering_3" value={form.Sub_metering_3} onChange={handleChange} />
            </div>
          </div>

          <button className="predict-btn" onClick={handleSubmit} disabled={loading}>
            {loading ? "Predicting..." : `Predict for ${state}`}
          </button>
        </div>

        <div className="result-card">
          {!result && !error && (
            <div className="result-empty">
              <div className="result-empty-icon">⚡</div>
              <span>Select your state and click Predict</span>
            </div>
          )}

          {error && <div className="error">{error}</div>}

          {result && (
            <>
              <div className="result-banner">
                <div className="result-label">Predicted Global Active Power</div>
                <div className="result-value">{result.predicted_power_kw}</div>
                <div className="result-unit">kilowatts (kW)</div>
                <div className="result-model">Model: {result.model} · {result.state}</div>
              </div>

              <div className={`result-interpretation ${interp.level}`}>
                {interp.text}
              </div>

              <div style={{
                display: "flex", justifyContent: "space-between",
                fontSize: 13, color: "#4b7a5e",
                background: "#f0fdf4", padding: "10px 14px", borderRadius: 8
              }}>
                <span>Monthly usage estimate</span>
                <strong style={{ color: "#14532d" }}>{result.estimated_monthly_kwh} kWh</strong>
              </div>
            </>
          )}
        </div>
      </div>

      {result && (
        <div className="cost-card">
          <p className="cost-title">
            Electricity Bill Estimator — {result.estimated_bill?.board} ({result.state})
          </p>

          <div className="cost-inputs">
            <div className="form-group">
              <label>Hours per day</label>
              <input type="number" min="1" max="24" value={hours}
                onChange={e => setHours(parseFloat(e.target.value))} />
            </div>
            <div className="form-group">
              <label>Number of days</label>
              <input type="number" min="1" max="365" value={days}
                onChange={e => setDays(parseFloat(e.target.value))} />
            </div>
            <div className="form-group">
              <label>Total units (kWh)</label>
              <input type="number" value={totalUnits} readOnly
                style={{ background: "#f0fdf4", color: "#15803d", fontWeight: 600 }} />
            </div>
          </div>

          <div className="cost-result">
            <div>
              <div style={{ fontSize: 11, color: "#15803d", marginBottom: 3, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Estimated Bill
              </div>
              <div className="cost-amount">
                <span>₹</span>{result.estimated_bill?.total_bill?.toLocaleString()}
              </div>
              <div className="cost-units">for {totalUnits} kWh over {days} days</div>
            </div>
            <div style={{ fontSize: 12, color: "#15803d", textAlign: "right" }}>
              {result.estimated_bill?.board}<br />
              <span style={{ opacity: 0.7 }}>domestic slab rates</span>
            </div>
          </div>

          <table className="slab-table">
            <thead>
              <tr>
                <th>Slab (units)</th>
                <th>Units</th>
                <th>Rate (₹/unit)</th>
                <th>Amount (₹)</th>
              </tr>
            </thead>
            <tbody>
              {result.estimated_bill?.slabs?.map((s, i) => (
                <tr key={i}>
                  <td>{s.slab}</td>
                  <td>{s.units}</td>
                  <td>₹{s.rate}</td>
                  <td>₹{s.cost}</td>
                </tr>
              ))}
              <tr>
                <td colSpan={3}>Total</td>
                <td>₹{result.estimated_bill?.total_bill}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}