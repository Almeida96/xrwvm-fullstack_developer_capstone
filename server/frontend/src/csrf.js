export async function csrfToken() {
  const response = await fetch("/djangoapp/csrf", {
    credentials: "same-origin",
  });
  if (!response.ok) throw new Error("Unable to start a secure session.");
  return (await response.json()).csrfToken;
}
