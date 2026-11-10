import React, { useEffect, useState } from "react";
import { api } from "../../api";
import "../assets/bootstrap.min.css";
export default function Header() {
  const [account, setAccount] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api("session")
      .then(setAccount)
      .catch(() => setAccount(null));
  }, []);
  async function logout() {
    try {
      await api("logout", {});
      window.location.assign("/");
    } catch (failure) {
      setError(failure.message);
    }
  }
  return (
    <header className="container py-3">
      <nav
        aria-label="Main navigation"
        className="d-flex gap-3 align-items-center flex-wrap"
      >
        <a href="/">Dealerships</a>
        {account?.authenticated ? (
          <>
            <span>Signed in as {account.username}</span>
            <button onClick={logout} className="btn btn-outline-dark">
              Log out
            </button>
          </>
        ) : (
          <>
            <a href="/login">Log in</a>
            <a href="/register">Register</a>
          </>
        )}
      </nav>
      {error && <p role="alert">{error}</p>}
    </header>
  );
}
