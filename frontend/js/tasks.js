let state = {
  skip: 0,
  limit: 10,
  status: "",
  search: "",
  editingId: null,
};

document.addEventListener("DOMContentLoaded", () => {
  if (!requireAuthOrRedirect()) return;

  document.getElementById("logout-btn").addEventListener("click", () => {
    clearToken();
    window.location.href = "index.html";
  });

  loadMe();

  const createForm = document.getElementById("create-task-form");
  createForm.addEventListener("submit", handleCreateTask);

  document.getElementById("status-filter").addEventListener("change", (e) => {
    state.status = e.target.value;
    state.skip = 0;
    loadTasks();
  });

  document.getElementById("search-input").addEventListener("input", debounce((e) => {
    state.search = e.target.value;
    state.skip = 0;
    loadTasks();
  }, 350));

  document.getElementById("prev-page").addEventListener("click", () => {
    state.skip = Math.max(0, state.skip - state.limit);
    loadTasks();
  });

  document.getElementById("next-page").addEventListener("click", () => {
    state.skip += state.limit;
    loadTasks();
  });

  loadTasks();
});

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

async function loadMe() {
  try {
    const me = await apiRequest("/auth/me");
    document.getElementById("current-user").textContent = `${me.email} (${me.role})`;
  } catch (err) {
    // handled globally by 401 redirect
  }
}

async function handleCreateTask(e) {
  e.preventDefault();
  const messageEl = document.getElementById("task-message");
  hideMessage(messageEl);

  const title = document.getElementById("new-task-title").value.trim();
  const description = document.getElementById("new-task-description").value.trim();
  const status = document.getElementById("new-task-status").value;
  const button = e.target.querySelector("button[type=submit]");

  setLoading(button, true, "Adding");
  try {
    await apiRequest("/tasks", {
      method: "POST",
      body: { title, description: description || null, status },
    });
    e.target.reset();
    showMessage(messageEl, "Task created.", "success");
    state.skip = 0;
    await loadTasks();
  } catch (err) {
    showMessage(messageEl, err.message, "error");
  } finally {
    setLoading(button, false, "Add Task");
  }
}

async function loadTasks() {
  const listEl = document.getElementById("task-list");
  const messageEl = document.getElementById("task-message");
  listEl.innerHTML = `<div class="empty-state">Loading tasks...</div>`;

  const params = new URLSearchParams({
    skip: state.skip,
    limit: state.limit,
    sort: "created_at",
  });
  if (state.status) params.set("status", state.status);
  if (state.search) params.set("search", state.search);

  try {
    const data = await apiRequest(`/tasks?${params.toString()}`);
    renderTasks(data);
  } catch (err) {
    showMessage(messageEl, err.message, "error");
    listEl.innerHTML = "";
  }
}

function renderTasks(data) {
  const listEl = document.getElementById("task-list");
  listEl.innerHTML = "";

  if (data.items.length === 0) {
    listEl.innerHTML = `<div class="empty-state">No tasks yet. Add one above to get started.</div>`;
  } else {
    for (const task of data.items) {
      listEl.appendChild(buildTaskElement(task));
    }
  }

  const totalPages = Math.max(1, Math.ceil(data.total / data.limit));
  const currentPage = Math.floor(data.skip / data.limit) + 1;
  document.getElementById("page-info").textContent = `Page ${currentPage} of ${totalPages} (${data.total} total)`;
  document.getElementById("prev-page").disabled = data.skip === 0;
  document.getElementById("next-page").disabled = data.skip + data.limit >= data.total;
}

function buildTaskElement(task) {
  const el = document.createElement("div");
  el.className = "task-item";

  el.innerHTML = `
    <div class="task-info">
      <h3>${escapeHtml(task.title)}</h3>
      ${task.description ? `<p>${escapeHtml(task.description)}</p>` : ""}
      <span class="badge ${task.status}">${task.status.replace("_", " ")}</span>
    </div>
    <div class="task-actions">
      <button class="secondary edit-btn">Edit</button>
      <button class="danger delete-btn">Delete</button>
    </div>
  `;

  el.querySelector(".edit-btn").addEventListener("click", () => startEdit(el, task));
  el.querySelector(".delete-btn").addEventListener("click", () => handleDelete(task.id, el));

  return el;
}

function startEdit(el, task) {
  el.className = "task-item editing";
  el.innerHTML = `
    <input type="text" class="edit-title" value="${escapeAttr(task.title)}" maxlength="255" required />
    <textarea class="edit-description" rows="2">${escapeHtml(task.description || "")}</textarea>
    <select class="edit-status">
      <option value="todo" ${task.status === "todo" ? "selected" : ""}>Todo</option>
      <option value="in_progress" ${task.status === "in_progress" ? "selected" : ""}>In Progress</option>
      <option value="done" ${task.status === "done" ? "selected" : ""}>Done</option>
    </select>
    <div class="task-actions">
      <button class="save-btn">Save</button>
      <button class="secondary cancel-btn">Cancel</button>
    </div>
  `;

  el.querySelector(".cancel-btn").addEventListener("click", () => loadTasks());
  el.querySelector(".save-btn").addEventListener("click", () => handleSaveEdit(el, task.id));
}

async function handleSaveEdit(el, taskId) {
  const messageEl = document.getElementById("task-message");
  hideMessage(messageEl);
  const title = el.querySelector(".edit-title").value.trim();
  const description = el.querySelector(".edit-description").value.trim();
  const status = el.querySelector(".edit-status").value;
  const saveBtn = el.querySelector(".save-btn");

  setLoading(saveBtn, true, "Saving");
  try {
    await apiRequest(`/tasks/${taskId}`, {
      method: "PUT",
      body: { title, description: description || null, status },
    });
    await loadTasks();
  } catch (err) {
    showMessage(messageEl, err.message, "error");
    setLoading(saveBtn, false, "Save");
  }
}

async function handleDelete(taskId, el) {
  const messageEl = document.getElementById("task-message");
  hideMessage(messageEl);

  if (!confirm("Delete this task? This cannot be undone.")) return;

  const deleteBtn = el.querySelector(".delete-btn");
  setLoading(deleteBtn, true, "Deleting");
  try {
    await apiRequest(`/tasks/${taskId}`, { method: "DELETE" });
    showMessage(messageEl, "Task deleted.", "success");
    await loadTasks();
  } catch (err) {
    showMessage(messageEl, err.message, "error");
    setLoading(deleteBtn, false, "Delete");
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function escapeAttr(str) {
  return escapeHtml(str).replace(/"/g, "&quot;");
}
