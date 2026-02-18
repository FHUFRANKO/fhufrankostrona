import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// Safe removal of Emergent badge (only the badge, not the entire DOM...)
const removeEmergentBadge = () => {
  const badge = document.getElementById("emergent-badge");
  if (badge) badge.remove();

  // In case the badge is injected as a link
  document.querySelectorAll("a[href*=\"emergent.sh\"]").forEach((el) => el.remove());
};

removeEmergentBadge();
document.addEventListener("DOMContentLoaded", removeEmergentBadge);

const container = document.getElementById("root");
const root = ReactDOM.createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
