import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";

function App() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [username, setUsername] = useState("");
    const [token, setToken] = useState(localStorage.getItem("token") || null);
    const [tasks, setTasks] = useState([]);
    const [task, setTask] = useState("");
    const [taskSchedule, setTaskSchedule] = useState("");
    const [status, setStatus] = useState("pending");
    const [isRegistering, setIsRegistering] = useState(false);

    // Fetch tasks when token is available
    const fetchTasks = useCallback(async () => {
        if (!token) return;
        
        const api = axios.create({
            baseURL: "http://localhost:8000",
            headers: { Authorization: `Bearer ${token}` },
        });

        try {
            const response = await api.get("/tasks");
            setTasks(response.data.tasks);
        } catch (error) {
            console.error("Failed to fetch tasks:", error.response?.data?.detail || error.message);
        }
    }, [token]); // ✅ Now only depends on `token`

    useEffect(() => {
        fetchTasks();
    }, [fetchTasks]);

    // API Request Handlers
    const registerUser = async () => {
        try {
            await axios.post("http://localhost:8000/register", { username, email, password });
            alert("User registered successfully!");
            setIsRegistering(false);
        } catch (error) {
            console.error(error);
            alert("Error: " + (error.response?.data?.detail || "Unknown error"));
        }
    };

    const loginUser = async () => {
        try {
            const response = await axios.post("http://localhost:8000/login", { email, password });
            const userToken = response.data.access_token;
            setToken(userToken);
            localStorage.setItem("token", userToken);
            alert("Login successful!");
        } catch (error) {
            console.error(error);
            alert("Error: " + (error.response?.data?.detail || "Login failed"));
        }
    };

    const logoutUser = () => {
        setToken(null);
        localStorage.removeItem("token");
        setTasks([]);
        alert("Logged out successfully!");
    };

    const addTask = async () => {
        const api = axios.create({
            baseURL: "http://localhost:8000",
            headers: { Authorization: `Bearer ${token}` },
        });

        try {
            await api.post("/add-task", { task_schedule: taskSchedule, task, status });
            alert("Task added successfully!");
            fetchTasks();
        } catch (error) {
            console.error(error);
            alert("Failed to add task.");
        }
    };

    const updateTask = async (taskId, newStatus) => {
        const api = axios.create({
            baseURL: "http://localhost:8000",
            headers: { Authorization: `Bearer ${token}` },
        });

        try {
            await api.put(`/update-task/${taskId}`, { status: newStatus });
            fetchTasks();
        } catch (error) {
            console.error(error);
            alert("Failed to update task.");
        }
    };

    const deleteTask = async (taskId) => {
        const api = axios.create({
            baseURL: "http://localhost:8000",
            headers: { Authorization: `Bearer ${token}` },
        });

        try {
            await api.delete(`/delete-task/${taskId}`);
            fetchTasks();
        } catch (error) {
            console.error(error);
            alert("Failed to delete task.");
        }
    };

    return (
        <div>
            <h1>Study Desk Assistant</h1>

            {!token ? (
                <>
                    <h2>{isRegistering ? "Register" : "Login"}</h2>
                    {isRegistering && (
                        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
                    )}
                    <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
                    <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                    {isRegistering ? (
                        <button onClick={registerUser}>Register</button>
                    ) : (
                        <button onClick={loginUser}>Login</button>
                    )}
                    <p>
                        {isRegistering ? "Already have an account?" : "Don't have an account?"}{" "}
                        <button onClick={() => setIsRegistering(!isRegistering)}>{isRegistering ? "Login" : "Register"}</button>
                    </p>
                </>
            ) : (
                <>
                    <button onClick={logoutUser} style={{ background: "red", color: "white" }}>Logout</button>

                    <h2>Task Management</h2>

                    <h3>Add Task</h3>
                    <input type="text" placeholder="Task" value={task} onChange={(e) => setTask(e.target.value)} />
                    <input type="datetime-local" value={taskSchedule} onChange={(e) => setTaskSchedule(e.target.value)} />
                    <select value={status} onChange={(e) => setStatus(e.target.value)}>
                        <option value="pending">Pending</option>
                        <option value="incomplete">Incomplete</option>
                        <option value="completed">Completed</option>
                    </select>
                    <button onClick={addTask}>Add Task</button>

                    <h3>Your Tasks</h3>
                    <button onClick={fetchTasks}>Load Tasks</button>
                    <ul>
                        {tasks.length > 0 ? (
                            tasks.map((task) => (
                                <li key={task._id}>
                                    {task.task} - {task.status} ({task.task_schedule}){" "}
                                    <button onClick={() => updateTask(task._id, "completed")}>Mark Completed</button>
                                    <button onClick={() => updateTask(task._id, "incomplete")}>Mark Incomplete</button>
                                    <button onClick={() => deleteTask(task._id)}>Delete</button>
                                </li>
                            ))
                        ) : (
                            <p>No tasks found. Click "Load Tasks".</p>
                        )}
                    </ul>
                </>
            )}
        </div>
    );
}

export default App;
