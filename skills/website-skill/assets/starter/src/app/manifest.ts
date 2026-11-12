import type { MetadataRoute } from "next";
import { site } from "@/lib/site";

export const dynamic = "force-static";

/* The icon comes from src/app/icon.png. Make it 512 by 512 pixels from the logo. */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: site.name,
    short_name: site.name,
    description: site.description,
    start_url: "/",
    display: "browser",
    background_color: site.backgroundColor,
    theme_color: site.themeColor,
    icons: [{ src: "/icon.png", sizes: "512x512", type: "image/png" }],
  };
}
