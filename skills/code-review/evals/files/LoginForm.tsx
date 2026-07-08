import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const API_KEY = "sk_live_9f8a7b6c5d4e3f2a1b0c";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [attempts, setAttempts] = useState(0);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // warn user after 30s of inactivity on the form
    setTimeout(() => {
      if (attempts > 0) {
        setError("You have made " + attempts + " attempts");
      }
    }, 30000);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("login attempt", email, password);
    setLoading(true);

    const res = await fetch("https://api.example.com/v1/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY,
      },
      body: JSON.stringify({ email: email, password: password }),
    });
    const data = await res.json();
    setLoading(false);

    if (data.token) {
      localStorage.setItem("auth_token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      if (data.user.isAdmin) {
        navigate("/admin");
      } else {
        navigate("/dashboard");
      }
    } else {
      setAttempts(attempts + 1);
      setError(data.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Sign in</h2>
      {error && (
        <div
          className="error-banner"
          dangerouslySetInnerHTML={{ __html: error }}
        />
      )}
      <input
        type="text"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">{loading ? "Signing in..." : "Sign in"}</button>
    </form>
  );
}
