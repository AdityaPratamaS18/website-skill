import Script from "next/script";
import { indexable } from "@/lib/seo";
import { site } from "@/lib/site";

/* Adds a tracker only on a launch build, and only if its ID exists. */
export default function Analytics() {
  if (!indexable) return null;
  return (
    <>
      {site.gaId && (
        <>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${site.gaId}`}
            strategy="afterInteractive"
          />
          <Script id="ga4" strategy="afterInteractive">
            {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${site.gaId}');`}
          </Script>
        </>
      )}
      {site.clarityId && (
        <Script id="clarity" strategy="lazyOnload">
          {`(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script","${site.clarityId}");`}
        </Script>
      )}
    </>
  );
}
