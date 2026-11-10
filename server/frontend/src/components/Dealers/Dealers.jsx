import React, { useEffect, useState } from "react";
import Header from "../Header/Header";
import { api } from "../../api";
export default function Dealers() {
  const [dealers, setDealers] = useState([]),
    [state, setState] = useState("All"),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(true);
  useEffect(() => {
    api("get_dealers")
      .then((data) => setDealers(data.dealers))
      .catch((failure) => setError(failure.message))
      .finally(() => setLoading(false));
  }, []);
  const visible =
    state === "All"
      ? dealers
      : dealers.filter((dealer) => dealer.state === state);
  return (
    <>
      <Header />
      <main className="container">
        <h1>Available dealerships</h1>
        <p>Browse the sample catalog and share a review.</p>
        <label>
          State{" "}
          <select
            className="form-select"
            value={state}
            onChange={(event) => setState(event.target.value)}
          >
            <option>All</option>
            {[...new Set(dealers.map((dealer) => dealer.state))]
              .sort()
              .map((value) => (
                <option key={value}>{value}</option>
              ))}
          </select>
        </label>
        {loading && <p role="status">Loading dealerships...</p>}
        {error && <p role="alert">{error}</p>}
        {!loading && !error && <p>{visible.length} dealerships</p>}
        <div className="row g-3">
          {visible.map((dealer) => (
            <article key={dealer.id} className="col-md-4">
              <div className="card card-body h-100">
                <h2 className="h5">
                  <a href={"/dealer/" + dealer.id}>{dealer.full_name}</a>
                </h2>
                <p>
                  {dealer.city}, {dealer.state}
                </p>
                <p>{dealer.address}</p>
              </div>
            </article>
          ))}
        </div>
      </main>
    </>
  );
}
