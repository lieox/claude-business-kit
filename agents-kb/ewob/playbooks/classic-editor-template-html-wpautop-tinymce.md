# Template HTML in WordPress Pages: wpautop, TinyMCE and REST Saves

**Source**: review of a live WordPress site, 01.11.2026 (headless Chromium DOM probes on the live site, WordPress core source from `WordPress/wordpress-develop` trunk)..
**Category**: playbooks
**Added**: 2026-11-01

## Core Insight
Pasting designed HTML (Lovable, Figma export, any template) into a classic-editor page works until three WordPress layers touch it: `wpautop` on render, TinyMCE in any visual editor, and the save filters on a REST write. Each one damages the same pattern, a link card (`<a>` wrapping block `<div>`s), in a different way. Know what each layer does before you write CSS against that markup or edit it.

## How It Works

### 1. wpautop on render (classic pages)
`the_content` runs `wpautop`. Source `<a class="card" href="x"><div class="img"></div><div class="body">...</div></a>` is served as `<a class="card" href="x"></p><div class="img"></div>...</div><p></a>`. The browser parser then builds:
- an empty `<p>` as the first child of the first card (its default bottom margin pushes the card content down);
- after each card, a sibling `<p>` holding an empty clone of the anchor, with the same class and href. In a flex row it is a thin sliver. In a CSS grid it takes a whole cell, so the grid becomes a checkerboard.
- The block children stay inside the real anchor, so `.card .img` selectors still match.

CSS cleanup that leaves the source alone (tested on a live site, no overflow, no lost cards):
```css
p:has(> .card:empty){display:none}
.card > p:empty{display:none}
```
An Elementor text-editor widget does NOT run wpautop on render. Its output equals the stored `editor` field.

### 2. TinyMCE (classic Visual tab and the Elementor panel text editor)
- The classic Visual tab empties an `<a>` that wraps block elements: `<a ...></a>` followed by the divs.
- "Edit with Elementor" on a classic page copies the whole `post_content` into one text-editor widget. After that, the widget's stored HTML had no anchors at all and each empty block div held a no-break space (seen on a live page: `post_content` still had the emptied anchors, the widget had none).
- Loosening `valid_elements` (a `tiny_mce_before_init` filter) is not proof that either editor is safe. Treat template pages as REST-only: never open them in a visual editor. If a page must stay editable in Elementor, put template HTML in an HTML widget (code editor, no TinyMCE) and check the render, because Kit styles aimed at the text-editor widget may stop applying.

### 3. REST saves
- **kses.** `content_save_pre` gets kses only when the user lacks `unfiltered_html` (`kses_init()` in `kses.php`). Without it, `<style>`, `<svg>`, `<button>` and `<input>` are stripped and their text stays on the page. Preflight without touching `/users`: `GET /wp/v2/<type>/<id>?context=edit&_fields=id,_links` and require the rel `wp:action-unfiltered-html`. WordPress compacts `https://api.w.org/` rels through `curies`, so the full URI is NOT a key in `_links` (a check on the full URI fails even for an admin; seen on a live site 01.11.2026). Accept either form.
- **`wp_targeted_link_rel`** (adds `rel="noopener"` on save) is deprecated since WordPress 6.7 and no longer hooked. On 6.7+ a `target="_blank"` link without `rel` survives a save unchanged.
- **Order inside `update_item`.** `wp_update_post()` runs first (fires `save_post`, so any purge-on-save hook), then terms, then `meta`. A purge hooked to `save_post` therefore fires BEFORE `_elementor_data` lands. A visitor in that gap can get the old render cached at the CDN. Purge again after the meta write and after the Elementor cache clear.
- **A no-change save** (POST with only `_fields`) still sets `post_modified` to now (`wp_insert_post`), which moves the Yoast sitemap `lastmod`, `article:modified_time` and schema `dateModified`. It stores no revision when nothing changed (`wp_save_post_revision_check_for_changes`).
- Writing `_elementor_data` through REST does not touch `post_content`, and on Elementor 4 the element cache keeps serving the old render until `DELETE /elementor/v1/cache` (see the ewob Log of 19.10.2026).

### 4. Attribute selectors against these hrefs
WordPress links Hebrew slugs percent-encoded. Hand-written hrefs often use uppercase hex and uppercase Latin words (`-PN-`, `Full-Face`) while the permalink is all lowercase. Match with `[href$="/<ENCODED-SLUG>/" i]`: the `i` flag makes hex and Latin case irrelevant, and the leading `/` stops one slug from matching the end of another. A raw (not encoded) Hebrew href would not match that selector.

## When to use
- Any WordPress page whose content is pasted template HTML, before writing CSS against its markup or editing it.
- Before a REST content write on a page that carries `<style>` or other non-post tags.
- When a site sits behind a CDN that caches HTML and a REST save is the refresh mechanism.

## Related
- [[elementor-verify-render-headless]]: verify the render, not the source.
