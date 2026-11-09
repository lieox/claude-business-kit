# 20 Reasons a Website/App Looks "Vibecoded"

**Source**: https://www.tiktok.com/@millee.md/video/7679967476544720148 (also: https://www.tiktok.com/@deonnahodges/video/7693573191146556702)
**Category**: playbooks
**Added**: 2026-09-14
**Updated**: 2026-10-08

## Core Insight
There is a recognizable, checklistable visual signature that makes an AI-built ("vibecoded") site or app look generic and AI-generated. Avoiding these patterns (or deliberately choosing them, but not by default) is a fast QA pass before shipping a design. Two creators independently converge on nearly the same list, which is itself evidence the signature is real and widely recognized, not one person's pet peeve. The second source also points at a maintained, named canonical reference and an automated scanner, not just a list to eyeball.

## How It Works
Visual/UI tells (merged from both sources):
1. Purple-to-blue (or indigo-to-blue) gradient (the default AI hero gradient)
2. Gradient hero text
3. Emojis in headings
4. Inter (also Geist/Roboto) font everywhere (the default AI font choice) - pick a heading typeface with character, keep body text simple
5. Colored left-border/side-stripe cards styled like permanent alerts - save the stripe treatment for real alerts/status, not decoration
6. Glassmorphism / frosted-glass cards and glowing halos or ambient spotlights behind sections - use spacing and contrast to show what matters instead
7. Low-contrast dark mode
8. Icon in a rounded-square tile above every heading / three (or more) identical icon-box feature cards in a row (the default AI features layout) - put the icon beside the heading or drop the container; group related ideas instead of tiling identical cards
9. A pill badge above the headline ("Introducing", "New") - delete it, or fold the useful info into the headline itself
10. Lucide icons everywhere (the default AI icon set)
11. Untouched shadcn UI (default component styling, unthemed)
12. Sections fading in as you scroll (default scroll animation) / pulsing dots, bouncy easing, hover zooms, auto-scrolling logo strips - only animate when something has actually changed
13. Cursor-following light beam
14. Buttons that fade on hover with no other interaction
15. Inconsistent spacing - conversely: related things should sit close together, and sections need clear space between them (a positive spacing rule, not just "avoid inconsistency")
16. Em dashes everywhere (a copy tell, not just a design tell)
17. Generic buzzword copy ("supercharge", "world-class", "next-generation", "Not a feature. A platform.") - say what the product does in plain words
18. Serif italics used for accent words
19. Space Grotesk + Instrument Serif font pairing (a specific default AI pairing)
20. Grain texture over a gradient
21. Giant hero stats ("10M+ users") with no context explaining what the number means
22. Tiny sequential-looking numbered labels (01, 02, 03) when nothing is actually a sequence
23. Beige/cream background with an oversized italic serif headline as an "escape" from the above, this is just the next cycle's version of the same genericness, not a real fix

Measurable accessibility/layout checks to run alongside the visual list: body text at least 16px, text contrast at least 4.5:1.

**Automated tooling**: Impeccable (free, open source) can scan a project for these tells directly: `npx impeccable install`, then `/impeccable init`, then `npx impeccable detect .` to list every instance found (with file and line). Its maintained reference list, the "slop catalog," lives at impeccable.style/slop (by Paul Bakaus) and is a living canonical source worth checking periodically, since AI-default styling trends shift (item 23 is itself an example of the list evolving).

**Ready-to-use audit prompt** (hand this to Claude Code on a finished build): "Audit this site for AI design tells. List every instance with file and line, then fix them, then re-check and tell me anything you kept on purpose. If you don't already know who the site is for and how it should feel, ask me before changing anything."

## Example
Source 1: a mock hero section is built up point-by-point on screen while each item is named, so each pattern maps to a visible before/after cue (e.g. item 19 shows the exact "Space Grotesk / Instrument Serif" font-pairing sample).

Source 2: a running numbered checklist burns on screen (left column, 1-15) while each item is demonstrated with a small mock UI panel on the right showing the exact pattern (e.g. "Build the Future" headline with "Color changes across the headline" labeled as gradient text; a "01 Discover / 02 Design / 03 Deliver" panel labeled "Tiny" for the numbered-label tell). Captioned with the full copy-paste audit prompt and the `npx impeccable` setup commands.

## When to Use
Run this as a checklist pass (or the automated `npx impeccable detect .` scan) on any client site or template before delivery: if 4+ of these are present unmodified from a scaffold/AI default, the site will read as generic/AI-built to anyone who has seen a few. Useful especially for landing pages built fast from a template or AI-generated starting point (ewob's HTML → Elementor pipeline). For a quick pass, hand the ready-to-use audit prompt above directly to the coding agent instead of manually checking each item.
