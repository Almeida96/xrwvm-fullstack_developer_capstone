import { csrfToken } from "./csrf";
export async function api(path, body) {
  const options = { credentials: "same-origin" };
  if (body !== undefined)
    Object.assign(options, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": await csrfToken(),
      },
      body: JSON.stringify(body),
    });
  const response = await fetch("/djangoapp/" + path, options);
  const data = await response.json();
  if (!response.ok)
    throw new Error(data.error || "The request could not be completed.");
  return data;
}
