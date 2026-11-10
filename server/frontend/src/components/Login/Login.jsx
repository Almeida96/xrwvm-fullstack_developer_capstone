import React, { useState } from "react";
import Header from "../Header/Header";
import { api } from "../../api";
export default function Login() {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const fields = new FormData(event.currentTarget);
    try {
      await api("login", {
        userName: fields.get("username"),
        password: fields.get("password"),
      });
      window.location.assign("/");
    } catch (failure) {
      setError(failure.message);
      setBusy(false);
    }
  }
  return (
    <>
      <Header />
      <main className="container">
        <h1>Log in</h1>
        <form
          onSubmit={submit}
          className="d-grid gap-3"
          style={{ maxWidth: 480 }}
        >
          <label>
            Username
            <input
              className="form-control"
              name="username"
              autoComplete="username"
              required
            />
          </label>
          <label>
            Password
            <input
              className="form-control"
              type="password"
              name="password"
              autoComplete="current-password"
              required
            />
          </label>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? "Signing in..." : "Log in"}
          </button>
          {error && <p role="alert">{error}</p>}
        </form>
      </main>
    </>
  );
}
