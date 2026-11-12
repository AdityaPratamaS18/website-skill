import type { MetadataRoute } from "next";
import { absoluteUrl, languageAlternates, localePath, plan } from "@/lib/seo";

export const dynamic = "force-static";

/* One row for each page. Language versions are alternates of that row.
   lastModified comes from the plan, never from the build time: a date that
   changes on each build tells search engines nothing. */
export default function sitemap(): MetadataRoute.Sitemap {
  return plan.pages
    .filter((p) => !p.noindex)
    .map((p) => {
      const languages = languageAlternates(p.route);
      const modified = p.updated ?? plan.approved_on;
      return {
        url: absoluteUrl(localePath(p.route)),
        ...(modified ? { lastModified: modified } : {}),
        changeFrequency: "monthly" as const,
        priority: p.route === "/" ? 1 : 0.8,
        ...(languages ? { alternates: { languages } } : {}),
      };
    });
}
