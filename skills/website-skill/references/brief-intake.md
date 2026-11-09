# Brief intake: procedure

## Accepted sources

| Source | How to read it |
|---|---|
| Filled discovery brief (.docx) | A Word skill or tool, or extract the XML text |
| Company profile, brochure (.pdf) | `Read` with `pages`, or a PDF skill |
| Proposal | Read the scope of work: page count, languages, included items |
| Current website | Fetch `sitemap.xml`, then each page |
| Chat notes, voice notes | Treat as a source, and write the date |

NOTE: The company profile often describes more of the business than the brief does. On one past project, the profile showed 3 divisions and the website showed 1.

## facts.md: structure

Write this file in short, plain sentences. It is an internal file. Put the source after each fact.

```markdown
# <Client>: facts sheet
Sources: <file names and dates>

## Business
- Legal name: ... (brief, section 3)
- Public name: ...
- Year started: ...
- Parent group: ...

## Contact (shown on the site)
- Phone, WhatsApp, email, address, hours, after-hours service

## Services (one row for each, in the order of commercial value)
| Service | What it includes | Who buys it | Proof | Source |

## Market
- Target locations, languages, buyer types

## Proof
- Certificates and approvals (with the exact name and number)
- Named clients (and permission to name them)
- Projects (client, scope, year, location)
- Figures (each one with its source)
- Testimonials (exact words, name, title, permission)

## Brand
- Logo file, colors, fonts, tone, sites that the client likes or dislikes

## Assets
- Photos by subject, video, documents

## Gaps
- Each missing fact, and the page that needs it

## Conflicts
- Each fact that has two values, with both sources
```

## Conflict rules

1. Read the notes for this client first, if they exist. A recorded decision settles a conflict.
2. Do not select a value yourself if 2 sources disagree and no decision exists.
3. Put the conflict in the questions file.
4. Record a build default for each open conflict, with this table in `facts.md`.
5. Use the legal name from the commercial registration in the schema `legalName`.

| Conflict | Sources | Build default until the client replies |
|---|---|---|
| Public phone number | Brief: A. Profile: B | Show the number from the newest source |
| A service that only one source names | Brief: yes. Profile: no | Leave it out |
| A claim, sector or figure | Any | Leave it out |

Show the user each build default at GATE 1.

## questions-for-client.md: structure

The client reads this file. Write it in plain business English, addressed to the client as "you".

1. Open on the fact. Do not use a courtesy opener such as "Thank you for your time" or "We understand that".
2. Put all open questions in one section near the top.
3. Write one direct question for each row, then what you will do with the answer.
4. Write requests as "Please supply", never "Client to supply".
5. Do not write about sources, earlier mistakes or the reasons for a question.
6. Show a gap as a benefit if that is true: "Do you hold partner status with Dell? If so, we will say so on the site."

Do not send this file. The user sends it.

## Current site

If the client has a website, do these steps too.

1. Fetch every URL in `sitemap.xml`, and the URLs in the menu.
2. Mark each URL as keep, merge or remove.
3. Put each URL that changes in `redirects` in the plan.
4. Record the current title and H1 of the pages that have Search Console traffic.

CAUTION: DO NOT DROP A URL WITHOUT A REDIRECT. THE SITE LOSES THE RANKINGS AND THE LINKS OF THAT URL.

Theme demo pages are common on old sites. On one past site, 39 of 53 URLs were demo content. Redirect these URLs, and do not carry over the content.
