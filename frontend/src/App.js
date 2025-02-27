import React, { useState } from "react";
import axios from "axios";

function App() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [username, setUsername] = useState("");
    const [token, setToken] = useState("");
    const [sessions, setSessions] = useState([]);

    const registerUser = async () => {
      try {
          console.log("Registering user:", { username, email, password }); // Debug log
  
          const response = await axios.post("http://localhost:8000/register", {
              username,
              email,
              password
          });
  
          console.log("Response Data:", response.data); // Debug API response
          alert("User registered successfully!");
      } catch (error) {
          console.error("API Call Error:", error.response?.data?.detail || error.message);
          alert("Error: " + (error.response?.data?.detail || "Unknown error"));
      }
  };
  

    const loginUser = async () => {
        try {
            const response = await axios.post("http://localhost:8000/login", {
                email,
                password
            });
            setToken(response.data.access_token);
            alert("Login successful!");
        } catch (error) {
            alert("Error: " + error.response?.data?.detail);
        }
    };

    const startStudySession = async () => {
        try {
            await axios.post("http://localhost:8000/start-session", {
                user_email: email,
                start_time: new Date().toISOString(),
                end_time: new Date(new Date().getTime() + 60 * 60000).toISOString(),
                distractions: 0,
                completed: false
            });
            alert("Study session started!");
        } catch (error) {
            alert("Error: " + error.response?.data?.detail);
        }
    };

    const fetchProgress = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/progress/${email}`);
            setSessions(response.data.study_sessions);
        } catch (error) {
            alert("Error: " + error.response?.data?.detail);
        }
    };

    return (
        <div>
            <h1>Study Desk Assistant</h1>

            <h2>Register</h2>
            <input type="text" placeholder="Username" onChange={(e) => setUsername(e.target.value)} />
            <input type="email" placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
            <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
            <button onClick={registerUser}>Register</button>

            <h2>Login</h2>
            <input type="email" placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
            <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
            <button onClick={loginUser}>Login</button>

            {token && (
                <>
                    <h2>Study Sessions</h2>
                    <button onClick={startStudySession}>Start Study Session</button>
                    <button onClick={fetchProgress}>Get Progress</button>
                    <ul>
                        {sessions.map((session, index) => (
                            <li key={index}>
                                Start: {session.start_time} | End: {session.end_time}
                            </li>
                        ))}
                    </ul>
                </>
            )}
        </div>
    );
}

export default App;
