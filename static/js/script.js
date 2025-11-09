const API = "https://campaign-tracker-qyql.onrender.com/api";



async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorBox = document.getElementById("loginError");

  errorBox.textContent = "";

  const res = await fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();

  if (res.ok) {
    localStorage.setItem("loggedIn", "true");

    document.getElementById("loginPage").classList.add("hidden");
    document.getElementById("mainPage").classList.remove("hidden");

    loadCampaigns();
    loadSummary();

    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
  } else {
    errorBox.textContent = data.error || "Invalid credentials";
  }
}


function logout() {
  localStorage.removeItem("loggedIn");
  document.getElementById("mainPage").classList.add("hidden");
  document.getElementById("loginPage").classList.remove("hidden");

  document.getElementById("username").value = "";
  document.getElementById("password").value = "";
}


window.addEventListener("DOMContentLoaded", () => {
  localStorage.removeItem("loggedIn");
  document.getElementById("mainPage").classList.add("hidden");
  document.getElementById("loginPage").classList.remove("hidden");
  checkFormFields();
});


async function loadCampaigns() {
  const q = document.getElementById("search").value || "";
  const res = await fetch(`${API}/campaigns?q=${q}`);
  const data = await res.json();

  const tbody = document.getElementById("tableBody");
  tbody.innerHTML = "";

  data.forEach(c => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${c.name}</td>
      <td>${c.client}</td>
      <td>${c.startDate}</td>
      <td>
        <select onchange="updateStatus('${c._id}', this)">
          <option ${c.status.trim() === "Active" ? "selected" : ""}>Active</option>
          <option ${c.status.trim() === "Paused" ? "selected" : ""}>Paused</option>
          <option ${c.status.trim() === "Completed" ? "selected" : ""}>Completed</option>
        </select>
      </td>
      <td><button class="delete-btn" onclick="confirmDelete('${c._id}', '${c.name}')">Delete</button></td>
    `;

    tbody.appendChild(row);

    
    const selectEl = row.querySelector("select");
    setStatusColor(selectEl);
  });
}


async function addCampaign() {
  const name = document.getElementById("name").value.trim();
  const client = document.getElementById("client").value.trim();
  const startDate = document.getElementById("startDate").value;
  const status = document.getElementById("status").value;

  if (!name || !client || !startDate) return alert("Please fill all fields");

  const res = await fetch(`${API}/campaigns`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, client, startDate, status })
  });

  const data = await res.json();
  if (res.ok) {
    showSuccessModal(`Campaign "${data.name}" added successfully!`);
    document.getElementById("name").value = "";
    document.getElementById("client").value = "";
    document.getElementById("startDate").value = "";
    checkFormFields();
    loadCampaigns();
    loadSummary();
  } else {
    alert(data.error || "Error adding campaign");
  }
}


async function updateStatus(id, selectEl) {
  const status = selectEl.value;
  setStatusColor(selectEl);

  await fetch(`${API}/campaigns/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status })
  });

  loadSummary();
}


function setStatusColor(selectEl) {
  selectEl.classList.remove("active", "paused", "completed");
  switch(selectEl.value.trim()) {
    case "Active": selectEl.classList.add("active"); break;
    case "Paused": selectEl.classList.add("paused"); break;
    case "Completed": selectEl.classList.add("completed"); break;
  }
}

let deleteId = null;
function confirmDelete(id, name) {
  deleteId = id;
  document.getElementById("deleteMessage").textContent = `Are you sure you want to delete "${name}"?`;
  document.getElementById("deleteModal").classList.remove("hidden");
}

document.getElementById("confirmYes").addEventListener("click", async () => {
  await fetch(`${API}/campaigns/${deleteId}`, { method: "DELETE" });
  document.getElementById("deleteModal").classList.add("hidden");
  loadCampaigns();
  loadSummary();
});

document.getElementById("confirmNo").addEventListener("click", () => {
  document.getElementById("deleteModal").classList.add("hidden");
});


function showSuccessModal(message) {
  document.getElementById("successMessage").textContent = message;
  document.getElementById("successModal").classList.remove("hidden");
}

document.getElementById("successOk").addEventListener("click", () => {
  document.getElementById("successModal").classList.add("hidden");
});


async function loadSummary() {
  const res = await fetch(`${API}/summary`);
  const s = await res.json();
  document.getElementById("total").textContent = s.total;
  document.getElementById("active").textContent = s.active;
  document.getElementById("paused").textContent = s.paused;
  document.getElementById("completed").textContent = s.completed;
}


document.getElementById("search").addEventListener("input", () => {
  clearTimeout(window._timer);
  window._timer = setTimeout(loadCampaigns, 400);
});


const addBtn = document.getElementById("addCampaignBtn");
const nameInput = document.getElementById("name");
const clientInput = document.getElementById("client");
const dateInput = document.getElementById("startDate");

function checkFormFields() {
  if (nameInput.value.trim() && clientInput.value.trim() && dateInput.value) {
    addBtn.disabled = false;
    addBtn.style.opacity = "1";
    addBtn.style.cursor = "pointer";
  } else {
    addBtn.disabled = true;
    addBtn.style.opacity = "0.6";
    addBtn.style.cursor = "not-allowed";
  }
}

[nameInput, clientInput, dateInput].forEach(input => {
  input.addEventListener("input", checkFormFields);
});
