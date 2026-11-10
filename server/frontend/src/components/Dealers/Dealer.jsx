import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Header from "../Header/Header";
import { api } from "../../api";
export default function Dealer() {
  const { id } = useParams();
  const [dealer, setDealer] = useState(null),
    [reviews, setReviews] = useState([]),
    [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    Promise.all([api("dealer/" + id), api("get_dealer_reviews/" + id)])
      .then(([data, entries]) => {
        if (active) {
          setDealer(data.dealer[0]);
          setReviews(entries);
        }
      })
      .catch((failure) => {
        if (active) setError(failure.message);
      });
    return () => {
      active = false;
    };
  }, [id]);
  return (
    <>
      <Header />
      <main className="container">
        {error && <p role="alert">{error}</p>}
        {!dealer && !error && <p>Loading dealership...</p>}
        {dealer && (
          <>
            <h1>{dealer.full_name}</h1>
            <p>
              {dealer.address}, {dealer.city}, {dealer.state}
            </p>
            <a className="btn btn-primary" href={"/postreview/" + id}>
              Write a review
            </a>
            <h2 className="mt-4">Reviews</h2>
            {reviews.length === 0 && <p>No reviews yet.</p>}
            {reviews.map((review) => (
              <article
                className="card card-body my-3"
                key={review.id || review._id}
              >
                <h3 className="h5">{review.name}</h3>
                <p>{review.review}</p>
                <small>
                  {review.car_make} {review.car_model} ({review.car_year})
                </small>
              </article>
            ))}
          </>
        )}
      </main>
    </>
  );
}
