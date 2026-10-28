# Security

Marineford Mart is an intentionally vulnerable CTF exercise, not a production application.

- Run it locally or inside an isolated, disposable lab that you own or are authorized to use.
- Do not expose it to the public internet.
- Do not use real credentials, personal information, or production data.
- Keep locally configured `SECRET_KEY`, `ACE_SECRET`, and `ENC_PARTS` values private.
- Keep `shop.db` and author-only solutions out of public commits.
- The SSTI sink, weak blacklist, client-trusted price, and challenge gate are deliberate vulnerabilities.

Report unintended issues privately to the repository owner with the affected route, impact, and reproduction steps. Do not include credentials or real user data in a report.
