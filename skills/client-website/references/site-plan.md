# Site plan: procedure and data

The site plan is the contract for the build. The code reads it and the gate checks the build against it.

## Page sets by business type

Start from the set. Remove a page if the facts do not support it.

| Business type | Pages |
|---|---|
| Service company (B2B, contractor, consultant) | Home, Services hub, 1 page for each service, About, Projects or Clients, Certifications (if any), Contact, Privacy |
| Trading, distribution, catalog | Home, Products hub, 1 page for each category, Sectors, About, Certifications, Contact, Privacy |
| Local business (clinic, salon, bakery) | Home, 1 page for each service, About, Gallery, Reviews, Contact, Privacy |
| Multi-city business | Add 1 page for each city, only if each page has local facts |
| Product, SaaS, app | Home, Features, Pricing, Comparison pages, Blog hub, Legal pages |
| Founder, personal brand | Home, About, Work, Writing, Contact |

CAUTION: DO NOT MAKE CITY PAGES THAT CHANGE ONLY THE CITY NAME. SEARCH ENGINES TREAT THESE PAGES AS DOORWAY PAGES.

## Keyword research

1. Make seed terms: each service or category, combined with each target location.
2. Use a keyword tool that is connected to this session (Ubersuggest, Semrush, Ahrefs or DataForSEO, for example).
3. Get volume and difficulty for the country of the client.
4. If no keyword tool is connected, ask the user for keyword data, or continue with no volume data.
5. Give each commercial page one primary keyword.
6. Add 3 to 8 secondary keywords that have the same search intent. Use them as H2 topics.
7. Read the top 5 results for each primary keyword of a main service. Record what these pages contain.
8. If the keyword tool gives no usable URLs, get the URLs with a web search.

Selection rules:

| Situation | Rule |
|---|---|
| New domain | Select terms with difficulty of 35 or less. Use 3 or more words in the term |
| Small market (Qatar, for example) | Low volumes are normal. A term with 40 to 110 searches a month is a valid target |
| Term with a different intent | Do not target it, even with high volume |
| Sub-type with low volume | Make it an H2 on the parent page. Do not make a new URL |
| Search tool not available | Set `volume` to null and tell the user at GATE 2 |
| All terms for a service show volume 0 | Keep the page, because the service needs a URL. Use the term that buyers use most in the brief. Tell the user at GATE 2 |
| 2 terms are possible | Select the term with the intent of a buyer. If the volumes are near, select the lower difficulty |
| High-volume term with an unclear intent | Read its top 5 results. Use it only if these results sell the same service |
| Country or city | Use the country for volume. Use the city only if the search tool has data for it and the business serves only that city |

NOTE: For example, the rice page of a food distributor targets the main term. Basmati, Sona Masoori and Matta are H2 groups on that page.

## Title and description rules

| Field | Rule |
|---|---|
| `title` | 30 to 60 characters. Primary keyword first. Brand name last if space permits |
| `description` | 120 to 160 characters. A fact, a proof point and a next action |
| `h1` | The name of the page in the words of the buyer. Different from the title |
| Route | Lower case and hyphens. Include the location only if the search term has it |

The home page title leads with the main keyword: "Business Consultancy in Dubai | Acme Advisors". The tagline of the brand goes in the Open Graph title of `site.ts` if needed.

## Data fields

| Field | Required | Meaning |
|---|---|---|
| `client` | Yes | Client name |
| `domain` | Yes | Canonical URL. `https`, no trailing slash, the final host |
| `deploy` | Yes | `static` or `server` |
| `keyword_source` | Yes | Tool and date, or `none` |
| `locales[]` | Yes | `key`, `hreflang`, `prefix`, `dir`, `default` |
| `approved_by`, `approved_on` | At GATE 2 | Name and date of the approval |
| `redirects[]` | If needed | `from` and `to` |
| `house_rules` | No | `no_dashes`, `no_eyebrows`. See `design-and-copy.md` |
| `pages[].route` | Yes | Path of the page in the default locale |
| `pages[].type` | Yes | `home`, `hub`, `service`, `category`, `location`, `landing`, `post`, `about`, `contact`, `team`, `projects`, `legal`, `utility` |
| `pages[].nav` | Yes | Short name for menus and breadcrumbs |
| `pages[].primary_keyword` | For commercial types | One unique term |
| `pages[].volume`, `difficulty` | For commercial types | Number, or null |
| `pages[].secondary[]` | No | H2 topics |
| `pages[].title`, `description`, `h1` | Yes | Exact text |
| `pages[].translations.<key>` | For each extra locale | `title`, `description`, `h1` |
| `pages[].noindex` | No | True for pages such as a thank-you page |

Commercial types are `home`, `service`, `category`, `location`, `landing` and `post`.
