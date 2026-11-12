import type { Metadata } from "next";
import rawPlan from "./site-plan.json";
import { site } from "./site";

type Copy = { title: string; description: string; h1: string };

export type PagePlan = Copy & {
  route: string;
  type: string;
  nav: string;
  noindex?: boolean;
  /* ISO date of the last real change to the page. The sitemap uses it. */
  updated?: string;
  translations?: Record<string, Copy>;
};

export type Locale = {
  key: string;
  hreflang: string;
  prefix: string;
  dir: string;
  default?: boolean;
};

export type SitePlan = {
  domain: string;
  approved_on?: string;
  locales: Locale[];
  pages: PagePlan[];
};

export const plan = rawPlan as unknown as SitePlan;

/* Preview builds stay out of search. Only a launch build sets SITE_INDEXABLE=1. */
export const indexable = process.env.SITE_INDEXABLE === "1";

export const defaultLocale = plan.locales.find((l) => l.default) ?? plan.locales[0];

export function getPage(route: string): PagePlan {
  const page = plan.pages.find((p) => p.route === route);
  if (!page) throw new Error(`Route ${route} is not in site-plan.json`);
  return page;
}

export function pageCopy(route: string, locale = defaultLocale.key): Copy {
  const page = getPage(route);
  if (locale === defaultLocale.key) return page;
  const copy = page.translations?.[locale];
  if (!copy) throw new Error(`Route ${route} has no ${locale} copy in site-plan.json`);
  return copy;
}

export function localePath(route: string, locale = defaultLocale.key) {
  const prefix = plan.locales.find((l) => l.key === locale)?.prefix ?? "";
  return `${prefix}${route === "/" ? "" : route}` || "/";
}

export function absoluteUrl(path: string) {
  return path === "/" ? plan.domain : `${plan.domain}${path}`;
}

/* One entry for each language version of a route, for metadata and the sitemap. */
export function languageAlternates(route: string) {
  if (plan.locales.length < 2) return undefined;
  const languages: Record<string, string> = {};
  for (const l of plan.locales) languages[l.hreflang] = absoluteUrl(localePath(route, l.key));
  languages["x-default"] = absoluteUrl(localePath(route));
  return languages;
}

type MetaOptions = {
  locale?: string;
  ogType?: "website" | "article";
  image?: string;
  publishedTime?: string;
  modifiedTime?: string;
};

export function pageMetadata(route: string, options: MetaOptions = {}): Metadata {
  const page = getPage(route);
  const { title, description } = pageCopy(route, options.locale);
  const path = localePath(route, options.locale);
  const image = absoluteUrl(options.image ?? site.ogImage);
  const openToSearch = indexable && !page.noindex;
  return {
    title: { absolute: title },
    description,
    alternates: { canonical: absoluteUrl(path), languages: languageAlternates(route) },
    robots: { index: openToSearch, follow: openToSearch },
    openGraph: {
      type: options.ogType ?? "website",
      siteName: site.name,
      title,
      description,
      url: absoluteUrl(path),
      images: [image],
      publishedTime: options.publishedTime,
      modifiedTime: options.modifiedTime,
    },
    twitter: { card: "summary_large_image", title, description, images: [image] },
  };
}

/* Removes empty strings, empty arrays and undefined values from a schema object. */
function compact<T>(value: T): T {
  if (Array.isArray(value)) return value.map(compact) as T;
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [key, item] of Object.entries(value)) {
      if (item === undefined || item === "") continue;
      if (Array.isArray(item) && item.length === 0) continue;
      out[key] = compact(item);
    }
    return out as T;
  }
  return value;
}

export function organizationLd() {
  const a = site.address;
  return compact({
    "@context": "https://schema.org",
    "@type": site.schemaType,
    "@id": `${site.url}/#organization`,
    name: site.name,
    legalName: site.legalName,
    description: site.description,
    url: site.url,
    logo: absoluteUrl(site.logo),
    image: absoluteUrl(site.ogImage),
    email: site.email,
    telephone: site.phone,
    foundingDate: site.foundingDate,
    slogan: site.tagline,
    address: {
      "@type": "PostalAddress",
      streetAddress: a.street,
      addressLocality: a.city,
      addressRegion: a.region,
      postalCode: a.postalCode,
      addressCountry: a.country,
    },
    geo:
      site.geo.lat !== null && site.geo.lng !== null
        ? { "@type": "GeoCoordinates", latitude: site.geo.lat, longitude: site.geo.lng }
        : undefined,
    hasMap: site.mapUrl,
    openingHours: site.openingHours,
    areaServed: site.areaServed,
    sameAs: site.social,
  });
}

/* Builds the trail from the plan. A parent path that is not in the plan is left out. */
export function breadcrumbLd(route: string, locale = defaultLocale.key) {
  const parts = route.split("/").filter(Boolean);
  const paths = ["/", ...parts.map((_, i) => `/${parts.slice(0, i + 1).join("/")}`)];
  const known = paths.filter((p) => plan.pages.some((page) => page.route === p));
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: known.map((path, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: getPage(path).nav,
      item: absoluteUrl(localePath(path, locale)),
    })),
  };
}

export function serviceLd(route: string, locale = defaultLocale.key) {
  const { h1, description } = pageCopy(route, locale);
  return compact({
    "@context": "https://schema.org",
    "@type": "Service",
    name: h1,
    description,
    url: absoluteUrl(localePath(route, locale)),
    provider: { "@id": `${site.url}/#organization` },
    areaServed: site.areaServed,
  });
}

type ArticleInput = {
  route: string;
  headline: string;
  description: string;
  published: string;
  updated?: string;
  image?: string;
};

export function articleLd(input: ArticleInput) {
  return compact({
    "@context": "https://schema.org",
    "@type": "Article",
    headline: input.headline,
    description: input.description,
    datePublished: input.published,
    dateModified: input.updated ?? input.published,
    image: input.image ? absoluteUrl(input.image) : undefined,
    author: { "@type": "Organization", name: site.legalName, url: site.url },
    publisher: { "@id": `${site.url}/#organization` },
    mainEntityOfPage: absoluteUrl(input.route),
  });
}

function plainText(text: string) {
  return text
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/[*_`]{1,3}/g, "")
    .trim();
}

export function faqLd(items: { q: string; a: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: plainText(f.a) },
    })),
  };
}
