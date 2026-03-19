import { useEffect, useState } from "react"
import axios from "axios"
import {
  BarChart, Bar, LineChart, Line, ComposedChart,
  XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, Cell
} from "recharts"

const API = "http://127.0.0.1:8000"

const WEATHER_CODES = {
  0:"Clear sky", 1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast",
  45:"Foggy", 51:"Light drizzle", 61:"Slight rain", 63:"Moderate rain",
  80:"Rain showers", 95:"Thunderstorm"
}

const CustomDot = (props) => {
  const { cx, cy, payload } = props
  if (payload.is_anomaly === 1)
    return <circle cx={cx} cy={cy} r={5} fill="#ef4444" stroke="#fff" strokeWidth={1.5} />
  return null
}

export default function Dashboard() {
  const [summary,   setSummary]   = useState(null)
  const [hourly,    setHourly]    = useState([])
  const [daily,     setDaily]     = useState([])
  const [weekly,    setWeekly]    = useState([])
  const [monthly,   setMonthly]   = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [weather,   setWeather]   = useState(null)
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState(null)

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [s, h, d, w, m, a, wx] = await Promise.all([
          axios.get(`${API}/stats/summary`),
          axios.get(`${API}/stats/hourly`),
          axios.get(`${API}/stats/daily`),
          axios.get(`${API}/stats/weekday-vs-weekend`),
          axios.get(`${API}/stats/monthly`),
          axios.get(`${API}/stats/anomalies`),
          axios.get(`${API}/realtime/weather`),
        ])
        setSummary(s.data)
        setHourly(h.data)
        setDaily(d.data.slice(-90))
        setWeekly(w.data)
        setMonthly(m.data)
        setAnomalies(a.data)
        setWeather(wx.data)
      } catch {
        setError("Cannot connect to API. Make sure FastAPI is running on port 8000.")
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  if (loading) return (
    <div className="loading">
      <div className="spinner"></div>
      Loading dashboard data...
    </div>
  )
  if (error) return <div className="error">{error}</div>

  const stats        = summary?.global_active_power
  const anomalyCount = anomalies.filter(r => r.is_anomaly === 1).length

  return (
    <div>
      <div className="page-header">
        <p className="page-title">Energy Consumption Dashboard</p>
        <p className="page-sub">
          {summary?.date_range?.start?.slice(0,10)} to {summary?.date_range?.end?.slice(0,10)}
          &nbsp;·&nbsp; {summary?.total_records?.toLocaleString()} hourly records
          &nbsp;·&nbsp; {anomalyCount} anomalies detected
        </p>
      </div>

      {weather && !weather.error && (
        <div className="weather-card">
          <div className="weather-temp">
            {weather.temperature_c}<span>°C</span>
          </div>
          <div className="weather-info">
            <div className="weather-loc">{weather.location}</div>
            <div className="weather-detail">
              {WEATHER_CODES[weather.weather_code] || "Clear"} &nbsp;·&nbsp;
              Feels like {weather.apparent_temp_c}°C &nbsp;·&nbsp;
              Humidity {weather.humidity_pct}% &nbsp;·&nbsp;
              Wind {weather.wind_speed_kmh} km/h
            </div>
            {weather.heat_factor_pct > 0 && (
              <div className="weather-heat-badge">
                +{weather.heat_factor_pct}% load due to heat
              </div>
            )}
          </div>
          <div className="weather-load">
            <div className="weather-load-label">Estimated load</div>
            <div className="weather-load-value">{weather.estimated_load_kw}</div>
            <div className="weather-load-unit">kW (weather-adjusted)</div>
          </div>
        </div>
      )}

      <div className="stat-grid">
        <div className="stat-card green">
          <div className="stat-icon green">⚡</div>
          <div className="stat-label">Mean Power</div>
          <div className="stat-value">{stats?.mean?.toFixed(2)}</div>
          <div className="stat-unit">kW average</div>
        </div>
        <div className="stat-card teal">
          <div className="stat-icon teal">📈</div>
          <div className="stat-label">Peak Power</div>
          <div className="stat-value">{stats?.max?.toFixed(2)}</div>
          <div className="stat-unit">kW maximum</div>
        </div>
        <div className="stat-card lime">
          <div className="stat-icon lime">📉</div>
          <div className="stat-label">Min Power</div>
          <div className="stat-value">{stats?.min?.toFixed(2)}</div>
          <div className="stat-unit">kW minimum</div>
        </div>
        <div className="stat-card amber">
          <div className="stat-icon amber">⚠️</div>
          <div className="stat-label">Anomalies</div>
          <div className="stat-value">{anomalyCount}</div>
          <div className="stat-unit">unusual days detected</div>
        </div>
      </div>

      <div className="chart-grid">
        <div className="chart-card full">
          <div className="chart-header">
            <span className="chart-title">Daily Average Power — Last 90 Days</span>
            <div className="anomaly-legend">
              <span><span className="legend-dot" style={{background:"#16a34a"}}></span>Normal</span>
              <span><span className="legend-dot" style={{background:"#ef4444"}}></span>Anomaly</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={230}>
            <ComposedChart data={anomalies.slice(-90)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#dcfce7" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={v => v.slice(5)} interval={8} />
              <YAxis tick={{ fontSize: 11 }} unit=" kW" />
              <Tooltip formatter={(v) => [`${v} kW`, "Power"]} labelFormatter={l => `Date: ${l}`} />
              <Line type="monotone" dataKey="avg_power_kw" stroke="#16a34a"
                dot={<CustomDot />} strokeWidth={2} name="avg_power_kw" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <span className="chart-title">Average Power by Hour</span>
            <span className="chart-badge">24h pattern</span>
          </div>
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={hourly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#dcfce7" />
              <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} unit=" kW" />
              <Tooltip formatter={v => [`${v} kW`, "Avg Power"]} />
              <Bar dataKey="avg_power_kw" radius={[4,4,0,0]}>
                {hourly.map((_, i) => (
                  <Cell key={i} fill={i >= 7 && i <= 22 ? "#16a34a" : "#0d9488"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <span className="chart-title">Weekday vs Weekend</span>
            <span className="chart-badge teal">hourly comparison</span>
          </div>
          <ResponsiveContainer width="100%" height={230}>
            <LineChart data={weekly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#dcfce7" />
              <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} unit=" kW" />
              <Tooltip formatter={v => [`${v} kW`]} />
              <Legend />
              <Line type="monotone" dataKey="weekday_kw" stroke="#16a34a" dot={false} strokeWidth={2} name="Weekday" />
              <Line type="monotone" dataKey="weekend_kw" stroke="#84cc16" dot={false} strokeWidth={2} name="Weekend" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card full">
          <div className="chart-header">
            <span className="chart-title">Monthly Average Power Consumption</span>
            <span className="chart-badge amber">seasonal trend</span>
          </div>
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#dcfce7" />
              <XAxis dataKey="month_name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 11 }} unit=" kW" />
              <Tooltip formatter={v => [`${v} kW`, "Avg Power"]} />
              <Bar dataKey="avg_power_kw" radius={[4,4,0,0]}>
                {monthly.map((row, i) => (
                  <Cell key={i} fill={
                    row.avg_power_kw > 1.3 ? "#ef4444" :
                    row.avg_power_kw > 1.1 ? "#f59e0b" : "#16a34a"
                  } />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}