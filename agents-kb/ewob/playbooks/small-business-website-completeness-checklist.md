# Small-Business Website Completeness Checklist (20 essentials)

**Source**: https://vt.tiktok.com/ZSVWeourA/ (canonical: https://www.tiktok.com/@yatesvids/video/7678849722475465992) (also: https://www.tiktok.com/@millee.md/video/7682550737234152724)
**Category**: playbooks
**Added**: 2026-08-29
**Updated**: 2026-09-14 - merged a second, technical/security-focused 20-item pre-launch list from a different creator (@millee.md) · 2026-10-31 - added "Search & AI visibility" (AI crawlers, llms.txt, Search Console)

## Core Insight
A local / small-business site is not "done" when it looks good, it is done when it has the trust, conversion, and technical-SEO pieces a real business site needs. This clip lists 20 items to hand a coding agent as a single "make no mistakes" instruction, doubling as a launch/definition-of-done checklist.

## How It Works
Framed as one prompt to Claude ("add all of these to my website"). The 20 items, grouped:

**Conversion & trust**
- Clear CTA above the fold
- Sticky mobile call-to-action
- Case studies section
- FAQ section
- Real photos of you and the team (not stock)
- Response-time promise (e.g. "we reply within X hours")
- Thank-you page shown after enquiries

**Pages & structure**
- Custom 404 page
- Internal links between pages
- Privacy policy page
- Maps + directions
- Breadcrumbs
- Unique page titles

**Technical SEO / metadata**
- Local business schema (structured data)
- Meta descriptions
- Robots.txt
- Alt text on images
- Social share images (OG images)
- Proper icons (favicon / touch icons)
- Google Analytics

**Technical & security (from the second list, @millee.md's "20 things to have Claude do before launching your website")**
- Terms & conditions page
- Get secrets off the frontend
- Force HTTPS
- Cookie consent banner
- Compress your images
- Check page load speed
- Fix color contrast
- Make it mobile friendly
- Fix broken links
- Form validation
- Spam protection

**Search & AI visibility (added 2026-10-31, from @jesseeisenbart's SEO list)**
- **AI crawlers are not blocked:** `robots.txt` (and any security plugin or CDN bot rule) allows GPTBot, ClaudeBot, PerplexityBot and Google-Extended unless the client asked otherwise. A site that blocks them cannot be cited in AI answers. Details and the bot list: the `ai-seo` and `hebrew-seo-geo-toolkit` skills.
- **`llms.txt` at the site root:** a short map of the main pages for AI readers (`hebrew-seo-geo-toolkit` has the format; `site-audit` already checks for it).
- **Google Search Console connected on launch day:** property verified, sitemap submitted, and the client's Google account added as owner. Without it nobody sees indexing errors.


## Example
The creator (@yatesvids) reads the whole list over 31 seconds while each item stacks on screen as caption text, positioning it as the "one message" you send an AI builder so nothing gets skipped before launch. A second, unrelated creator (@millee.md) posted the same format ("20 things to have Claude do before launching your website, in under 28 seconds") aimed explicitly at handing the list to an AI coding agent; roughly half his items duplicate the first list (privacy policy, meta titles/descriptions, social preview image, favicon, sitemap+robots.txt, alt text, custom 404, analytics, one clear CTA) and the rest add the technical/security layer merged above.

## When to Use
As a pre-launch QA pass on any client site, or as a checklist appended to a build brief. Overlaps with, and complements, [intake-spec-form-to-upgraded-brief](./intake-spec-form-to-upgraded-brief.md): that file covers the local-SEO page structure (עמוד-על per type + FAQ Schema), this one is the item-level "did we ship the essentials" list. Several items (local business schema, meta descriptions, unique titles, robots.txt, breadcrumbs, alt text) are the same technical-SEO layer that a winning local site needs. The merged technical/security group (HTTPS, secrets off frontend, cookie consent, form validation, spam protection, page speed, color contrast) is the layer to check right before a client site goes live, complementing [avoid-vibecoded-website-look](./avoid-vibecoded-website-look.md), the visual/design QA pass from the same second creator.
