function togglePassword(el) {
  const pwd = document.getElementById("password");
  if (pwd.type === "password") {
    pwd.type = "text";
    el.textContent = "Hide";
  } else {
    pwd.type = "password";
    el.textContent = "Show";
  }
}

/* Modal functions */
function openSupportModal() {
  document.getElementById("supportModal").style.display = "block";
}

function closeSupportModal() {
  document.getElementById("supportModal").style.display = "none";
}

// Close modal when clicking outside
window.onclick = function(event) {
  const modal = document.getElementById("supportModal");
  if (event.target === modal) {
    modal.style.display = "none";
  }
}

