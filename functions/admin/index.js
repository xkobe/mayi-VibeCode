import { html } from "../_lib/util.js";
import { uiHtml } from "./_ui.js";

export async function onRequest() {
  return html(uiHtml);
}
