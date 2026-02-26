import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
function App() {
  const [isAdminView, setIsAdminView] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Hello! I am your Order Support Agent. This is all of your orders' }
  ]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [requests, setRequests] = useState([]);
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/products`);
        setProducts(response.data.products);
      } catch (error) {
        console.error("Cannot load list of products:", error);
      }
    };

    fetchProducts();
  }, []);
  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMessages = [...messages, { role: 'user', text: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, { message: input });
      setMessages([...newMessages, { role: 'ai', text: response.data.response }]);
    } catch (error) {
      setMessages([...newMessages, { role: 'ai', text: "Server connection error!" }]);
    } finally {
      setLoading(false);
    }
  };

  const fetchRequests = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/admin/requests`);
      setRequests(res.data);
    } catch (err) { console.error(err); }
  };

  const handleApprove = async (id) => {
    try {
      await axios.post(`${API_BASE_URL}/admin/approve/${id}`);
      alert("Order Approved!");
      fetchRequests();
    } catch (err) { alert("Failed!"); }
  };
  const handleRefuse = async (id) => {
    try {
      await axios.post(`${API_BASE_URL}/admin/refuse/${id}`);
      alert("Request Refused!");
      fetchRequests();
    } catch (err) { alert("Failed!"); }
  };

  useEffect(() => {
    if (isAdminView) fetchRequests();
  }, [isAdminView]);

  return (
    <div className="container">
      <div className="nav">
        <button
          className={`nav-btn ${!isAdminView ? 'active' : ''}`}
          onClick={() => setIsAdminView(false)}>User</button>
        <button
          className={`nav-btn ${isAdminView ? 'active' : ''}`}
          onClick={() => setIsAdminView(true)}>Admin</button>
      </div>

      <div className="card">
        <div className="header">
          <div className="sparkle">✦</div>
          <h2>{isAdminView ? "Admin Dashboard" : "AI Agent Support"}</h2>
        </div>

        {!isAdminView ? (
          <>
            <div className="chat-box">
              {messages.map((m, i) => (
                <div key={i} className={`msg ${m.role === 'user' ? 'msg-user' : 'msg-ai'}`}>
                  <div className="role-label">
                    {m.role === 'user' ? 'ME' : 'AI Assistant'}
                  </div>
                  <div style={{ marginBottom: '12px' }}>{m.text}</div>
                  {m.role === 'ai' && i === 0 && (
                    <div className="order-list-mini" style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '6px',
                      paddingTop: '10px'
                    }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: '0 10px',
                        marginBottom: '2px'
                      }}>
                        <span style={{ fontSize: '0.7em', fontWeight: 'bold', color: '#888', textTransform: 'uppercase' }}>Order Name</span>
                        <span style={{ fontSize: '0.7em', fontWeight: 'bold', color: '#888', textTransform: 'uppercase' }}>Status</span>
                      </div>
                      {products.map((p) => (
                        <div key={p.id} style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          backgroundColor: 'rgba(255, 255, 255, 0.6)',
                          padding: '6px 10px',
                          borderRadius: '8px',
                          fontSize: '0.85em',
                          boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                        }}>
                          <span style={{ fontWeight: '500', color: '#444' }}>{p.id}</span>
                          <span style={{
                            fontWeight: 'bold',
                            color: p.status === 'Success' ? '#27ae60' : '#f39c12',
                            textTransform: 'uppercase',
                            fontSize: '0.75em'
                          }}>
                            {p.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {loading && <div className="msg msg-ai" style={{ opacity: 0.5 }}>...</div>}
            </div>

            <div className="input-area">
              <input
                className="input-field"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask me anything about your projects"
              />
              <button className="send-btn" onClick={sendMessage}>➤</button>
            </div>
          </>
        ) : (
          <div className="admin-content">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ORDER</th>
                  <th>ACTION</th>
                  <th>COMMAND</th>
                </tr>
              </thead>
              <tbody>
                {requests.map(req => (
                  <tr key={req[0]}>
                    <td style={{ fontWeight: '600', fontSize: '13px', color: '#666666' }}>{req[1]}</td>
                    <td style={{ fontSize: '13px', color: '#666' }}>{req[2]}</td>
                    <td>
                      <button className="approve-btn" onClick={() => handleApprove(req[0])} style={{ backgroundColor: '#d7ecff' }}>
                        Approve
                      </button>
                      <button className="refuse-btn" onClick={() => handleRefuse(req[0])} style={{}}>Refuse</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {requests.length === 0 && <p style={{ textAlign: 'center', color: '#ccc', marginTop: '50px' }}>No pending tasks.</p>}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;