document.addEventListener("DOMContentLoaded", () => {
  if (getToken()) {
    window.location.href = "dashboard.html";
    return;
  }

  const loginTab = document.getElementById("login-tab");
  const registerTab = document.getElementById("register-tab");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const messageEl = document.getElementById("auth-message");

  function activateLoginTab() {
    loginTab.classList.add("active");
    registerTab.classList.remove("active");
    loginForm.style.display = "flex";
    registerForm.style.display = "none";
  }

  function activateRegisterTab() {
    registerTab.classList.add("active");
    loginTab.classList.remove("active");
    registerForm.style.display = "flex";
    loginForm.style.display = "none";
  }

  loginTab.addEventListener("click", () => {
    activateLoginTab();
    hideMessage(messageEl);
  });

  registerTab.addEventListener("click", () => {
    activateRegisterTab();
    hideMessage(messageEl);
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideMessage(messageEl);
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    const button = loginForm.querySelector("button[type=submit]");
    setLoading(button, true, "Logging in");
    try {
      const data = await apiRequest("/auth/login", {
        method: "POST",
        form: true,
        body: { username: email, password },
      });
      setToken(data.access_token);
      window.location.href = "dashboard.html";
    } catch (err) {
      showMessage(messageEl, err.message, "error");
    } finally {
      setLoading(button, false, "Log In");
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideMessage(messageEl);
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const button = registerForm.querySelector("button[type=submit]");
    setLoading(button, true, "Registering");
    try {
      await apiRequest("/auth/register", { method: "POST", body: { email, password } });
      registerForm.reset();
      activateLoginTab();
      showMessage(messageEl, "Registration successful! Please log in.", "success");
    } catch (err) {
      showMessage(messageEl, err.message, "error");
    } finally {
      setLoading(button, false, "Register");
    }
  });
});
