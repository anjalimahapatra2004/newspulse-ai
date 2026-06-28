function setFieldError(fieldEl, message) {
  fieldEl.classList.add("has-error");
  fieldEl.querySelector(".error-text").textContent = message;
}

function clearFieldError(fieldEl) {
  fieldEl.classList.remove("has-error");
}

function setButtonLoading(button, isLoading) {
  button.disabled = isLoading;
  button.classList.toggle("loading", isLoading);
}

function goToDashboard(name, email) {
  localStorage.setItem("newspulse_name", name);
  localStorage.setItem("newspulse_email", email);
  window.location.href = "dashboard.html";
}

/* ---------------- Password visibility toggle ---------------- */
const EYE_OPEN = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/></svg>`;
const EYE_CLOSED = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a18.6 18.6 0 0 1 4.22-5.06M9.9 4.24A10.4 10.4 0 0 1 12 4c7 0 11 7 11 7a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;

function setupPasswordToggles() {
  document.querySelectorAll(".toggle-password").forEach((btn) => {
    btn.innerHTML = EYE_OPEN;
    btn.addEventListener("click", () => {
      const input = document.getElementById(btn.dataset.target);
      const showing = input.type === "text";
      input.type = showing ? "password" : "text";
      btn.innerHTML = showing ? EYE_OPEN : EYE_CLOSED;
      btn.classList.remove("pulse-once");
      requestAnimationFrame(() => btn.classList.add("pulse-once"));
    });
  });
}
setupPasswordToggles();

/* ---------------- Google sign-in ---------------- */
// Called by Google's Identity Services script after a successful sign-in.
// Must stay a global function - Google's library calls it by name.
async function handleGoogleSignIn(response) {
  try {
    const data = await api.googleLogin(response.credential);
    localStorage.setItem("newspulse_token", data.access_token);
    showToast(`Welcome, ${data.name.split(" ")[0]}!`, "success");
    setTimeout(() => goToDashboard(data.name, data.email), 500);
  } catch (err) {
    showToast(err.message || "Google sign-in failed. Please try again.", "error");
  }
}


const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const emailField = document.getElementById("login-email-field");
    const passwordField = document.getElementById("login-password-field");
    clearFieldError(emailField);
    clearFieldError(passwordField);

    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    const button = document.getElementById("login-submit");

    setButtonLoading(button, true);
    try {
      const data = await api.login({ email, password });
      localStorage.setItem("newspulse_token", data.access_token);
      showToast(`Welcome back, ${data.name.split(" ")[0]}!`, "success");
      setTimeout(() => goToDashboard(data.name, data.email), 600);
    } catch (err) {
      if (err.message.toLowerCase().includes("password")) {
        setFieldError(passwordField, err.message);
      } else if (err.message.toLowerCase().includes("email") || err.message.toLowerCase().includes("account")) {
        setFieldError(emailField, err.message);
      } else {
        showToast(err.message, "error");
      }
    } finally {
      setButtonLoading(button, false);
    }
  });
}

/* ---------------- Signup ---------------- */
const signupForm = document.getElementById("signup-form");
if (signupForm) {
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const nameField = document.getElementById("signup-name-field");
    const emailField = document.getElementById("signup-email-field");
    const passwordField = document.getElementById("signup-password-field");
    [nameField, emailField, passwordField].forEach(clearFieldError);

    const name = document.getElementById("signup-name").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;
    const button = document.getElementById("signup-submit");

    if (password.length < 8) {
      setFieldError(passwordField, "Password must be at least 8 characters.");
      return;
    }

    setButtonLoading(button, true);
    try {
      const data = await api.signup({ name, email, password });
      localStorage.setItem("newspulse_token", data.access_token);
      showToast(`Welcome to NewsPulse AI, ${name.split(" ")[0]}!`, "success");
      setTimeout(() => goToDashboard(data.name, data.email), 600);
    } catch (err) {
      if (err.message.toLowerCase().includes("email")) {
        setFieldError(emailField, err.message);
      } else {
        showToast(err.message, "error");
      }
    } finally {
      setButtonLoading(button, false);
    }
  });
}

/* ---------------- Forgot password ---------------- */
const forgotForm = document.getElementById("forgot-form");
if (forgotForm) {
  forgotForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("forgot-email").value.trim();
    const button = document.getElementById("forgot-submit");

    setButtonLoading(button, true);
    try {
      const data = await api.forgotPassword({ email });
      showToast(data.message, "success", 4500);
      forgotForm.reset();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setButtonLoading(button, false);
    }
  });
}

/* ---------------- Reset password ---------------- */
const resetForm = document.getElementById("reset-form");
if (resetForm) {
  resetForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const passwordField = document.getElementById("reset-password-field");
    clearFieldError(passwordField);

    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    const newPassword = document.getElementById("reset-password").value;
    const button = document.getElementById("reset-submit");

    if (!token) {
      showToast("This reset link is invalid. Please request a new one.", "error");
      return;
    }
    if (newPassword.length < 8) {
      setFieldError(passwordField, "Password must be at least 8 characters.");
      return;
    }

    setButtonLoading(button, true);
    try {
      const data = await api.resetPassword({ token, new_password: newPassword });
      showToast(data.message, "success");
      setTimeout(() => (window.location.href = "login.html"), 1200);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setButtonLoading(button, false);
    }
  });
}

/* ---------------- Logout (used on dashboard) ---------------- */
function logout() {
  localStorage.removeItem("newspulse_token");
  localStorage.removeItem("newspulse_name");
  localStorage.removeItem("newspulse_email");
  showToast("Logged out successfully", "success", 1500);
  setTimeout(() => (window.location.href = "login.html"), 500);
}