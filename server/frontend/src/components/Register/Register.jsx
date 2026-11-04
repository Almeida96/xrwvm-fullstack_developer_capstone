import React, { useState } from "react";
import Header from "../Header/Header";
import "./Register.css";

const emptyForm = { userName: "", firstName: "", lastName: "", email: "", password: "" };

export default function Register() {
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch("/djangoapp/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify(form),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok || result.error) {
        throw new Error(result.error || "Registration failed. Please try again.");
      }
      setSuccess("Registration completed. You can now log in.");
      setForm(emptyForm);
    } catch (err) {
      setError(err.message || "Unable to register. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <Header />
      <main className="register-main">
        <section className="register-card" aria-labelledby="registration-title">
          <h1 id="registration-title">Register</h1>
          <p>Create an account to review dealerships and share your experience.</p>

          <form className="register-form" onSubmit={handleSubmit}>
            <div className="register-field">
              <label htmlFor="username">Username</label>
              <input id="username" name="userName" type="text" autoComplete="username"
                value={form.userName} onChange={handleChange} required />
            </div>
            <div className="register-field">
              <label htmlFor="firstName">First Name</label>
              <input id="firstName" name="firstName" type="text" autoComplete="given-name"
                value={form.firstName} onChange={handleChange} required />
            </div>
            <div className="register-field">
              <label htmlFor="lastName">Last Name</label>
              <input id="lastName" name="lastName" type="text" autoComplete="family-name"
                value={form.lastName} onChange={handleChange} required />
            </div>
            <div className="register-field">
              <label htmlFor="email">Email</label>
              <input id="email" name="email" type="email" autoComplete="email"
                value={form.email} onChange={handleChange} required />
            </div>
            <div className="register-field">
              <label htmlFor="password">Password</label>
              <input id="password" name="password" type="password" autoComplete="new-password"
                minLength={8} value={form.password} onChange={handleChange} required />
            </div>

            {error && <p className="register-error" role="alert">{error}</p>}
            {success && <p className="register-success" role="status">{success}</p>}

            <button className="register-submit" type="submit" disabled={loading}>
              {loading ? "Registering..." : "Register"}
            </button>
          </form>

          <p className="register-login">
            Already have an account? <a href="/login">Log in</a>
          </p>
        </section>
      </main>
    </div>
  );
}
