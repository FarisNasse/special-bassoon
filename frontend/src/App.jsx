import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';

// Updated Plotly Imports for Vite
import Plotly from 'plotly.js/dist/plotly';
import createPlotlyComponent from 'react-plotly.js/factory';

// Use .default if the import ends up as an object (Vite workaround)
const Plot = typeof createPlotlyComponent === 'function' 
  ? createPlotlyComponent(Plotly) 
  : createPlotlyComponent.default(Plotly);

function App() {
  const [file, setFile] = useState(null)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://127.0.0.1:5000/analyze', formData);
      setData(res.data);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error processing file. Check console.");
    }
    setLoading(false);
  };

  return (
    <div className="container mt-5">
      <h1 className="mb-4">Finance Dashboard</h1>
      
      {/* Upload Section */}
      <div className="card p-4 mb-4">
        <div className="input-group">
          <input type="file" className="form-control" onChange={handleFileChange} accept=".csv" />
          <button className="btn btn-primary" onClick={handleUpload} disabled={loading}>
            {loading ? 'Processing...' : 'Analyze Finances'}
          </button>
        </div>
      </div>

      {data && (
        <>
          {/* Anomaly Alerts */}
          {data.anomalies.length > 0 && (
            <div className="alert alert-warning">
              <h4>⚠️ Spending Alerts</h4>
              <ul>
                {data.anomalies.map((a, i) => (
                  <li key={i}>{a.message}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="row">
            {/* Chart 1: Where your money goes (Sunburst) */}
            <div className="col-md-6 mb-4">
              <div className="card p-2">
                <h5>Where your money goes</h5>
                <Plot
                  data={[{
                    type: "sunburst",
                    labels: data.summary.map(d => d.category),
                    parents: data.summary.map(() => ""), // Top level
                    values: data.summary.map(d => d.amount),
                    outsidetextfont: {size: 20, color: "#377eb8"},
                    leaf: {opacity: 0.4},
                    marker: {line: {width: 2}},
                  }]}
                  layout={{width: 500, height: 500, margin: {l: 0, r: 0, b: 0, t: 0}}}
                />
              </div>
            </div>

            {/* Chart 2: Monthly Trend (Bar) */}
            <div className="col-md-6 mb-4">
              <div className="card p-2">
                <h5>Monthly Spending Trend</h5>
                <Plot
                  data={[{
                    x: data.trend.map(d => d.month),
                    y: data.trend.map(d => d.amount),
                    type: 'bar',
                    marker: {color: 'orange'}
                  }]}
                  layout={{width: 500, height: 500, title: 'Total Spend per Month'}}
                />
              </div>
            </div>
          </div>

          {/* Raw Data Table */}
          <div className="card p-4">
            <h5>Recent Transactions</h5>
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Category</th>
                  <th>Description</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                {data.raw_data.map((row, i) => (
                  <tr key={i}>
                    <td>{new Date(row.date).toLocaleDateString()}</td>
                    <td>{row.category}</td>
                    <td>{row.desc}</td>
                    <td>${row.amount.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}

export default App