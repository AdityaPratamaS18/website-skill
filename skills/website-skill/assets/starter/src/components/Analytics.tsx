import Script from "next/script";
import { indexable } from "@/lib/seo";
import { site } from "@/lib/site";

/* Consent Mode v2 defaults. They must run before the GA4 config call.
   Ad storage stays denied, because the starter has no ad tags. If the site
   has a consent banner, the banner calls gtag('consent','update',{...})
   when the visitor accepts. */
function consentDefaults() {
  const analytics = site.consent.analytics;
  const wait = analytics === "denied" ? ",wait_for_update:500" : "";
  return `gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'${analytics}'${wait}});`;
}

/* One delegated listener for the whole page. It sends a GA4 event for each
   lead action: a phone link, a WhatsApp link, an email link and a form submit.
   The browser fires submit only after the form validation passes. */
const leadEvents = `(function(){
function send(name,params){if(typeof window.gtag==='function')window.gtag('event',name,params);}
document.addEventListener('click',function(e){
var a=e.target&&e.target.closest?e.target.closest('a[href]'):null;if(!a)return;
var h=a.getAttribute('href')||'';var p={link_url:h,link_text:(a.textContent||'').trim().slice(0,100)};
if(h.indexOf('tel:')===0)send('click_call',p);
else if(/^https?:\\/\\/(wa\\.me|api\\.whatsapp\\.com|wa\\.link)\\//.test(h))send('click_whatsapp',p);
else if(h.indexOf('mailto:')===0)send('click_email',p);
},true);
document.addEventListener('submit',function(e){
var f=e.target;if(!f||f.tagName!=='FORM')return;
send('generate_lead',{form_id:f.id||f.getAttribute('name')||'form'});
},true);
})();`;

/* Adds a tracker only on a launch build, and only if its ID exists. */
export default function Analytics() {
  if (!indexable) return null;
  return (
    <>
      {site.gaId && (
        <>
          <Script id="ga4" strategy="afterInteractive">
            {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}window.gtag=gtag;${consentDefaults()}gtag('js',new Date());gtag('config','${site.gaId}');`}
          </Script>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${site.gaId}`}
            strategy="afterInteractive"
          />
          <Script id="ga4-lead-events" strategy="afterInteractive">
            {leadEvents}
          </Script>
        </>
      )}
      {site.clarityId && (
        /* Do not change this id to "clarity". The browser makes each element id
           a global, so window.clarity becomes the script element and Clarity
           never loads. Check typeof window.clarity === "function" on the live site. */
        <Script id="microsoft-clarity" strategy="lazyOnload">
          {`(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script","${site.clarityId}");`}
        </Script>
      )}
    </>
  );
}
