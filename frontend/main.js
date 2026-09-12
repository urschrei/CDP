// Entry point of the front-end bundle. esbuild writes main.css next to main.js.
import "./main.css";
import htmx from "htmx.org";

// The templates do not use hx-on or "js:" values. The stylesheet styles the
// request indicators.
htmx.config.allowEval = false;
htmx.config.includeIndicatorStyles = false;
