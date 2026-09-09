# generedge.com

Static website for GenerEdge, Inc. — replaces the previous WordPress + Elementor
site. Plain HTML/CSS/JS, no runtime dependencies.

**Live: <https://ejcorral3s.github.io/Generedge-Website/>**

Published automatically to GitHub Pages on every push to the default branch,
and deployable to Hostinger as a plain file copy. The Pages build is marked
`noindex` until the site runs on its real domain — see *Deploying*.

> **Working on this with Claude Code? Read [`CLAUDE.md`](./CLAUDE.md) first.**
> It has the project context, the house rules, and what is still outstanding.

---

## Quick start

```bash
# Build the pages from src/
python3 scripts/build.py

# Check structure, links, assets and accessibility
python3 scripts/check.py

# Preview locally
python3 -m http.server 8000
# → http://localhost:8000
```

## Editing

Edit page bodies in `src/`, then re-run `python3 scripts/build.py`.

Shared header, footer, `<head>`, meta tags and the cookie banner live in
`scripts/build.py`. The root-level `.html` files are generated output — editing
them directly gets your work overwritten.

## Pages

| URL | Source |
|---|---|
| `/` | `src/index.html` |
| `/business-loans/` | `src/business-loans.html` |
| `/about-us/` | `src/about-us.html` |
| `/contact-us/` | `src/contact-us.html` |
| `/privacy-policy/` | `src/privacy-policy.html` |
| `/terms-and-conditions/` | `src/terms-and-conditions.html` |
| `/cookies-policy/` | `src/cookies-policy.html` |
| `404` | `src/404.html` |

---

## Where the forms go

The three lead forms (builder application on the home page, business financing
application, and the contact form) all post to whatever is configured in the
`FORM` dict at the top of `scripts/build.py`:

```python
FORM = {
    "provider": "formsubmit",
    "email": "info@generedge.com",
    ...
}
```

**Current setup: `formsubmit`.** Each submission is emailed to
`info@generedge.com`. There is no account, no API key and no server — it works
from any static host.

> ### One-time activation — the only step left before leads arrive
> FormSubmit will not deliver to an address it has not verified. The **first**
> POST to a new address makes it email `info@generedge.com` an activation link
> instead; clicking that link once turns delivery on permanently.
>
> Trigger it deliberately, so the first real visitor is not the one who pays for
> it:
>
> ```bash
> curl -X POST https://formsubmit.co/ajax/info@generedge.com \
>   -H 'Content-Type: application/json' \
>   -d '{"Form":"Setup test","Message":"Activating the generedge.com contact forms."}'
> ```
>
> Then open `info@generedge.com` and click the confirmation link. Send one more
> test through the live contact form to confirm it lands.
>
> Until that happens nothing is lost: an unverified address makes the send fail,
> and the form falls back to the phone number, the email address and a
> "Send it by email instead" link carrying everything the visitor typed.

### Switching provider

Change `FORM["provider"]` and re-run the build. No JavaScript changes needed.

| provider | what to set | notes |
|---|---|---|
| `formsubmit` | `email` | default. No signup; one-time activation as above. |
| `web3forms` | `access_key` | free key emailed to you by web3forms.com. The key is public by design — it only permits posting to your own inbox. |
| `formspree` | `endpoint` | your `https://formspree.io/f/xxxx` URL. |
| `custom` | `endpoint` | any URL accepting a JSON `POST`. Use this for the Close CRM worker described in `CLAUDE.md`. |

Whatever the provider, **a lead is never silently lost**: if the request fails,
the form shows the phone number and email address plus a "Send it by email
instead" link that opens the visitor's mail client pre-filled with everything
they typed.

Every form also carries a honeypot field, inline `aria-invalid` errors, an
`aria-live` status region, a disabled-while-sending guard, and fires a
`generate_lead` GA event on success.

---

## Deploying

### GitHub Pages (automatic)

**Live at <https://ejcorral3s.github.io/Generedge-Website/>.**

`.github/workflows/deploy-pages.yml` builds and publishes on every push to the
default branch. Other branches get the build and the checks as CI but publish
nothing.

Pages serves the repository from the **`gh-pages`** branch, which holds only
generated output — never edit it by hand, the next deploy replaces it. Building
into a branch rather than a Pages deployment is deliberate: pushing a branch
needs only the `contents: write` permission a workflow can grant itself, while
the deployment API needs Pages to have been switched on by an account with admin
rights first.

The site is served from `https://<user>.github.io/<repo>/`, so the workflow
works out that sub-path from the repository name, builds with `GE_BASE` set to
it, and every internal URL is rewritten to match. Nothing in `src/` needs to
know about it — which is also why nothing in `src/` may hardcode
`https://generedge.com/...`; write root-relative links like `/about-us/`.

github.io builds are marked `noindex, nofollow`. A project site cannot serve a
robots.txt that crawlers will read (they only fetch
`https://<user>.github.io/robots.txt`, which belongs to the user site), so
without the meta tag this would become a fully indexable duplicate of a
financial services site competing with generedge.com in search. The tag flips to
`index, follow` automatically as soon as the build runs against a real domain.

### Moving to generedge.com

1. Add a `CNAME` file at the repo root containing `generedge.com`.
2. Set the domain under **Settings → Pages**.
3. Point the DNS records at GitHub Pages.

`GE_BASE` then resolves to empty, URLs return to domain-root form and the pages
become indexable — all from the CNAME file, with no workflow edit.

### Hostinger

The committed root-level HTML is already built for a domain root, so deployment
is a plain file copy. Either connect this repo under **Websites → Advanced →
Git**, or upload the contents of `_site/` (run `python3 scripts/package.py`
first) to `public_html/`.

`.htaccess` must go up with it — it carries the legacy 301 redirects.

### Build configuration

| Variable | Default | Purpose |
|---|---|---|
| `GE_ORIGIN` | `https://generedge.com` | scheme + host used for canonicals, Open Graph and the sitemap |
| `GE_BASE` | *(empty)* | sub-path the site is served under, e.g. `/Generedge-Website` |

```bash
# what GitHub Pages publishes
GE_ORIGIN=https://ejcorral3s.github.io GE_BASE=/Generedge-Website python3 scripts/build.py
```

---

## Scripts

| Script | Purpose |
|---|---|
| `scripts/build.py` | assembles `src/` + shared chrome into the root HTML, `sitemap.xml` and `robots.txt` |
| `scripts/check.py` | structure, links, referenced assets, forms and accessibility checks |
| `scripts/package.py` | copies the publishable subset into `_site/` |
| `scripts/fetch-assets.sh` | re-pulls the original images from the old WordPress site |
| `scripts/make-social-images.py` | regenerates `og-default.png` and `apple-touch-icon.png` (needs Pillow; optional) |

---

## Still outstanding before the domain moves

- [ ] **Activate FormSubmit** — run the curl above, then click the link that arrives at `info@generedge.com`
- [ ] Set the real GA4 measurement ID in `SITE["ga_id"]` — analytics stay off until then
- [ ] Tracey signs off on the copy flagged in `CLAUDE.md` §4 — including the
      SMS consent checkbox becoming optional, the 4 msgs/mo frequency, and the
      removal of the "Over $15 million" fee tier
- [ ] Legal review of the three policy pages
- [ ] Confirm `handshake.jpg` stock photo licensing
- [ ] DNS: replicate MX/SPF/DKIM/DMARC **before** switching nameservers
- [ ] Submit `sitemap.xml` in Google Search Console

Done during the rebuild: real images pulled off WordPress, branded social card
and touch icon generated, forms connected, GitHub Pages deployment wired up,
legacy 301s written. A designer can replace `og-default.png` and
`apple-touch-icon.png` at any time — nothing else depends on how they look.

## Browser support

Modern evergreen browsers. Degrades gracefully: without JavaScript, all content
and navigation still work — only the scroll reveals, animated counters, mobile
menu and client-side form validation are lost.
