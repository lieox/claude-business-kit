# AI tells in English

**Two sources, and they are not equal.**

1. **The on-screen prompt** in the TikTok logged as #019 (@sabrina_ramonov, captured
   25.08.2026). Transcribed from the video frames, not from her DM funnel. One creator's
   list. Reorganized and annotated here; the rules are hers.
2. 🆕 **[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)**,
   the field guide maintained by WikiProject AI Cleanup (added 27.08.2026 from item #061).
   Community-maintained and revised as models change, which makes it the stronger source.
   ⚠️ It carries its own "needs updating" notice for the newest models as of August 2026.

**Both sources are framed by their authors as ways to beat AI detectors. Ignore that
framing entirely.** Detector scores are not evidence in either direction. Everything below
is for writing quality, and for one thing detectors never check: whether the text asserts
something it cannot support.

**Sections marked 🆕 are from Wikipedia and are wired into `scan_ai_tells.py`.** The four
groups below the original list are the ones that matter most for client work, because they
are credibility failures before they are style failures.

---

## SHOULD

- Use clear, simple language
- Use short, impactful sentences
- Use active voice, avoid passive voice
- Use bullet lists in social media posts
- Focus on practical, actionable insights
- Use data and specific examples to support claims where possible
- Use "you" and "your" to directly address the reader
- Vary sentence length and sentence structure naturally
- Prefer specific nouns, numbers, examples, and actions over abstract language
- Sound like a person with a point of view, not a neutral summary engine

## AVOID: punctuation and formatting

- Em dashes anywhere. Use commas, periods, parentheses, or standard punctuation
- Semicolons
- Markdown clutter and stray asterisks
- Hashtags
- Unnecessary adjectives and adverbs
- Output warnings or notes. Give the requested output

## AVOID: giveaway sentence patterns

- `not just X, but also Y`
- `it's not X. it's Y.`
- Repetitive contrast formulas such as `while X, Y` throughout the response
- Broad generalizations
- Metaphors and cliches
- Rhetorical questions used as transitions
- Fake conversational transitions: `here's the thing`, `here's where it gets interesting`,
  `think about it`, `let that sink in`
- Dramatic one-line fragments inserted only for emphasis
- Excessive parenthetical explanations
- Excessive qualification and hedging
- Restating the user's question before answering
- Summarizing your own response at the end unless asked
- Repeating the same idea in the introduction, body, and ending

## AVOID: structural symmetry

- Starting multiple paragraphs with the same grammatical structure
- Making every paragraph roughly the same length
- Making every sentence roughly the same length
- Overly symmetrical lists where every bullet follows the exact same pattern
- Forced groups of three items
- Excessive headings and subheadings
- Generic headings such as `Key Takeaways`, `Why It Matters`, `Benefits`, `Final Thoughts`
- Common setup language such as `In conclusion`, `In closing`, `The key takeaway`
- Ending sections with generic inspirational or reflective statements

## AVOID: filler and padding

- Filler sentences whose only purpose is transitioning to the next point
- Explaining obvious implications
- Sounding overly complete, exhaustive, balanced, or sanitized
- Adding context the reader does not need in order to understand the answer
- Polished corporate language where ordinary language works
- Generic claims without a concrete example, number, person, event, or action
- Treating both sides of every issue as equally important when the evidence favors one side
- Unnatural vocabulary variation where a simple repeated term would sound more human
- Repeating keywords or phrases when a natural alternative exists

## AVOID: these words

can, may, just, that, very, really, literally, actually, certainly, probably, basically,
could, maybe, delve, embark, enlightening, esteemed, shed light, craft, crafting, imagine,
realm, game-changer, unlock, discover, skyrocket, abyss, not alone, in a world where,
revolutionize, disruptive, utilize, utilizing, dive deep, tapestry, illuminate, unveil,
pivotal, intricate, elucidate, hence, furthermore, realm, however, harness, exciting,
groundbreaking, cutting-edge, remarkable, it, remains to be seen, glimpse into, navigating,
landscape, stark, testament, in summary, in conclusion, moreover, boost, skyrocketing,
opened up, powerful, inquiries, ever-evolving

**Caveat on this word list.** It is blunt and partly wrong. `can`, `may`, `just`, `that`,
`it`, and `however` are ordinary English and cannot be banned outright; the original prompt
overreached. The scanner flags them at low severity only. Treat the list as candidates and
judge each in context. The high-value entries are the inflated ones: delve, tapestry,
realm, unlock, harness, pivotal, groundbreaking, revolutionize, game-changer, dive deep,
testament, landscape, ever-evolving.

## IMPORTANT (final pass)

- Review the response and ensure no em dashes
- If several consecutive sentences have similar length or structure, rewrite some of them
- Prefer slight natural variation over perfect structural consistency

---

## 🆕 Inflated significance (Wikipedia)

The dominant tell in AI-written business, place, and "about us" copy. The text keeps
telling you something matters instead of showing what it does.

`boasts a` (meaning "has") · `nestled in the heart of` · `vibrant town` ·
`rich cultural heritage` · `stands as a testament to` · `marking a pivotal moment in the
evolution of` · `represented a significant shift toward` · `part of a broader movement` ·
`solidify its role as a regional hub` · `breathtaking region`

**Fix:** replace the claim of importance with the fact that would make a reader conclude it.
"boasts a 20-year heritage" becomes "opened in 2006".

## 🆕 Vague attribution (Wikipedia)

`industry reports` · `observers have cited` · `experts argue` · `some critics argue` ·
`studies show` · `research suggests` · `several sources` · `it is widely believed` ·
`is of interest to researchers`

**This is a credibility failure, not a style one.** In a client deliverable it is worse
than clumsy writing: it asserts authority that has no source behind it. Either name the
source or delete the claim.

## 🆕 Formulaic conclusions (Wikipedia)

`Despite its [positive quality], [subject] faces challenges...` ·
`Despite these challenges, [subject] continues to...` · `Looking ahead` ·
`Future Outlook` as a heading · `Challenges and Legacy` as a heading ·
`only time will tell` · `remains to be seen`

The pattern is a closing paragraph that balances the piece without adding anything. Cut it
and end on the last real sentence.

## 🆕 Citation and sourcing damage (Wikipedia)

The category the original list has nothing about, and the only one that can actually harm a
client:

- **Fabricated sources.** Confident citations to work that does not exist
- Broken external links; DOIs and ISBNs that are invalid or resolve to something unrelated
- Book citations with no page number
- `utm_source=` left in a URL, which means the link was copied from a share button rather
  than from the source
- Named references declared and never used

**Every citation in a client-facing document gets opened before the document ships.** No
exceptions, and no "it looks right".

## 🆕 Machine voice and placeholders (Wikipedia)

`as of my last update` · `as of my knowledge cutoff` · `my training data` ·
`as an AI language model` · collaborative phrasing that addresses "the user" ·
`lorem ipsum` · `[insert ...]` · `[Client Name]` · `TODO:` · `TBD`

**Highest stakes of any group here**, because it is the one a reader recognizes instantly
as unedited machine output. Related: `feedback_internal_blocks_leak_to_clients`.

## 🆕 Era vocabulary (Wikipedia)

Wikipedia tracks the overused vocabulary by model generation, which is more useful than one
flat list because the tells rotate:

| Era | Words |
|---|---|
| 2023 to mid-2024 | additionally, delve, intricate, pivotal, underscore, tapestry, testament |
| mid-2024 to 2025 | align with, enhance, emphasizing, fostering, highlighting |
| mid-2025 onward | emphasizing, enhance, showcasing, highlighting |
| throughout | crucial, key, enduring, garner, underscore (as a verb) |

The mid-2025 group is the live one. It is scored MED, not HIGH, because these are ordinary
English words that only read as a tell when they cluster.

## 🆕 Re-check of the Wikipedia page, 31.10.2026 (revid 1382925076)

The page had 40+ edits in the ten days before this check. What was new against the 27.08 version:

**Copula avoidance (WP:AINOCOPULA).** `serves as` · `stands as` · `functions as` · `operates as` ·
`represents` · `marks` in place of "is", and `boasts` / `features` / `offers` / `maintains` in
place of "has". One study found a 10%+ drop in "is"/"are" in academic writing in 2023. In ad
copy "offers" is often legitimate, so judge it. **Fix:** "is" and "has", or what the thing does.

**"Y rather than X" (reversed negative parallelism).** "Particularly common in recent LLM
output", with examples from April and October 2026. Also the mid-2026 **corrective framings**:
"should be treated as X rather than Y", "the available information does not establish",
"should not be confused with". **Fix:** say what it is. Drop the contrast.

**Vague connection (WP:AICONNECT).** `associated with` · `connected to` · `in connection with`
instead of stating the relation ("was the CEO of"). **Fix:** name the relation.

**Superficial analysis.** A trailing "-ing" clause that comments on significance:
"..., highlighting / underscoring / reflecting / contributing to / fostering ...". Newer
search-enabled models pin it on a named source that never said it. **Fix:** cut the clause.

**Promotional tone is now subtle.** Older models wrote "the best". Newer ones are "more subtly
positive" and avoid obvious superlatives. Word lists catch less of it, so read for tone.

**Style markup.** Emoji at the start of headings or list items · Title Case Headings ·
curly quotes (“ ” ‘ ’) · inline-header lists (already covered below).

**Em dash moved to "historical indicators (2022 to September 2026)".** Most new models suppress
it. But a July 2026 study found that of current models **only Claude** uses em dashes more than
professional writers. For drafts written here the ban stays, and it targets exactly the right model.

**Not signs (WP "Ineffective indicators").** Perfect grammar · a mix of casual and formal
register · "bland" or "robotic" prose · "fancy" vocabulary. None of these mark AI text, and
"fixing" them makes human writing worse. Do not flag them.

---

## 🆕 Client-facing structure and tone (antislop-copywriting, MIT, added 10.10.2026)

The same failures as Hebrew sections 10 to 13, for English drafts.

| Avoid | Fix |
|-------|-----|
| Chatbot closers: "I hope this helps", "Let me know if you have any questions", "Feel free to reach out", "Happy to help" | Delete, or name the actual next step |
| Fake-candid openers: "Honestly,", "To be honest", "Let's be real" | Delete the opener, say the thing |
| Signposting: "Let's break it down", "Here's what you need to know" | Delete, start with the content |
| Staccato drama: "Simple. Fast. Done." | One normal sentence |
| Tailing negation: "A plan, not a package." | Say what it is with a verb |
| False ranges: "from strategy to execution" | Name what is actually done |
| Inline-header bullets: `- **Label:** text` everywhere | Sentences that start with their subject |
| Numbered sections and "(see point 5)" inside an email | One short paragraph per topic, repeat the word instead of pointing |
