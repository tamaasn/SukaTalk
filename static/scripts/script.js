function switchToSignup() {
    document.getElementById("login-form").classList.add("hidden");
    document.getElementById("signup-form").classList.remove("hidden");
  }
  
  function switchToLogin() {
    document.getElementById("signup-form").classList.add("hidden");
    document.getElementById("login-form").classList.remove("hidden");
  }
  
  document.getElementById("login-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
  
    const storedUser = JSON.parse(localStorage.getItem(username));
    if (!storedUser || storedUser.password !== password) {
      alert("Login gagal. Cek kembali username dan password.");
      return;
    }
  
    alert(`Selamat datang, ${storedUser.name}!`);
  });
  
  document.getElementById("signup-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const name = document.getElementById("signup-name").value;
    const username = document.getElementById("signup-username").value;
    const password = document.getElementById("signup-password").value;
  
    if (localStorage.getItem(username)) {
      alert("Username sudah digunakan.");
      return;
    }
  
    const newUser = { name, username, password };
    localStorage.setItem(username, JSON.stringify(newUser));
    alert("Akun berhasil dibuat! Silakan login.");
    switchToLogin();
  });
  