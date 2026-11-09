import type { MetadataRoute } from "next";
import { absoluteUrl, languageAlternates, localePath, plan } from "@/lib/seo";

export const dynamic = "force-static";

/* One row for each page. Language versions are alternates of that row. */
export default function sitemap(): MetadataRoute.Sitemap {
  return plan.pages
    .filter((p) => !p.noindex)
    .map((p) => {
      const languages = languageAlternates(p.route);
      return {
        url: absoluteUrl(localePath(p.route)),
        lastModified: new Date(),
        changeFrequency: "monthly" as const,
        priority: p.route === "/" ? 1 : 0.8,
        ...(languages ? { alternates: { languages } } : {}),
      };
    });
}
