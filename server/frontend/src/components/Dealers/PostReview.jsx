import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Header from "../Header/Header";
import { api } from "../../api";
export default function PostReview() {
  const { id } = useParams();
  const [cars, setCars] = useState([]),
    [dealer, setDealer] = useState(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [ready, setReady] = useState(false);
  useEffect(() => {
    Promise.all([api("dealer/" + id), api("get_cars"), api("session")])
      .then(([data, catalog, account]) => {
        setDealer(data.dealer[0]);
        setCars(catalog.CarModels);
        if (!account.authenticated)
          throw new Error("Log in before posting a review.");
        setReady(true);
      })
      .catch((failure) => setError(failure.message));
  }, [id]);
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const fields = new FormData(event.currentTarget),
      car = cars.find((value) => String(value.id) === fields.get("car"));
    try {
      if (!car) throw new Error("Choose a car model.");
      await api("add_review", {
        dealership: Number(id),
        review: fields.get("review"),
        purchase_date: fields.get("date"),
        purchase: fields.get("purchase") === "true",
        car_make: car.CarMake,
        car_model: car.CarModel,
        car_year: car.CarYear,
      });
      window.location.assign("/dealer/" + id);
    } catch (failure) {
      setError(failure.message);
      setBusy(false);
    }
  }
  return (
    <>
      <Header />
      <main className="container">
        <h1>Review {dealer?.full_name || "dealership"}</h1>
        {error && <p role="alert">{error}</p>}
        <form
          className="d-grid gap-3"
          style={{ maxWidth: 640 }}
          onSubmit={submit}
        >
          <label>
            Your review
            <textarea
              name="review"
              className="form-control"
              maxLength={5000}
              required
            />
          </label>
          <label>
            Visit or purchase date
            <input name="date" className="form-control" type="date" required />
          </label>
          <label>
            Car model
            <select name="car" className="form-select" required defaultValue="">
              <option value="" disabled>
                Choose a car
              </option>
              {cars.map((car) => (
                <option key={car.id} value={car.id}>
                  {car.CarMake} {car.CarModel} ({car.CarYear})
                </option>
              ))}
            </select>
          </label>
          <label>
            Did you purchase the car?
            <select name="purchase" className="form-select">
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </label>
          <button className="btn btn-primary" disabled={!ready || busy}>
            {busy ? "Saving..." : "Post review"}
          </button>
        </form>
      </main>
    </>
  );
}
