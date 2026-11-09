import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Analytics from "@/components/Analytics";
import JsonLd from "@/components/JsonLd";
import { defaultLocale, organizationLd } from "@/lib/seo";
import { site } from "@/lib/site";

/* Replace this font at the design step. Use a maximum of 2 families. */
const body = Inter({ variable: "--font-body", subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  applicationName: site.name,
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang={defaultLocale.key} dir={defaultLocale.dir} className={body.variable}>
      <body>
        <JsonLd data={organizationLd()} />
        {/* Add the site header here. */}
        <main id="main">{children}</main>
        {/* Add the site footer here. */}
        <Analytics />
      </body>
    </html>
  );
}
