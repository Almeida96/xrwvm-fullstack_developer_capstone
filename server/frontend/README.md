# React dealership client

This client uses the Django API described in the [repository README](../../README.md). It includes catalog filtering, dealer details, reviews and account forms.

Requires Node.js 22.12 or later. Run `npm ci` and `npm run dev`; Django must run on port 8000. Add the exact Vite browser origin to Django's `DJANGO_CSRF_TRUSTED_ORIGINS` environment variable. `npm run build` writes `dist/`.

All review and authentication writes fetch a CSRF token from Django first. The header reads the session endpoint rather than trusting browser storage. React escapes displayed review text. No sentiment model is used by this interface.
