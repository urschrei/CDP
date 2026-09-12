// Entry point of the front-end bundle. esbuild writes main.css next to main.js.
import "./main.css";
import htmx from "htmx.org";

// The templates do not use hx-on or "js:" values. The stylesheet styles the
// request indicators.
htmx.config.allowEval = false;
htmx.config.includeIndicatorStyles = false;

// The search page sends status 503, with a message, when search is not
// available. Swap that response. Other status codes keep the default handling.
htmx.config.responseHandling = [
  { code: "204", swap: false },
  { code: "[23]..", swap: true },
  { code: "503", swap: true, error: true },
  { code: "[45]..", swap: false, error: true },
  { code: "...", swap: false },
];

// Do not send empty fields in GET requests. The pushed URLs then contain only
// the filters and the query in use.
document.addEventListener("htmx:configRequest", (event) => {
  const { parameters, verb } = event.detail;
  if (verb !== "get") {
    return;
  }
  for (const [name, value] of Object.entries(parameters)) {
    if (value === "") {
      delete parameters[name];
    }
  }
});
