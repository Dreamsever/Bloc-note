let tasks = [];
const titleInput = document.getElementById("list-title");

const displayTitle = document.getElementById("display-title");
const taskInput = document.getElementById("task_input");
const addButton = document.getElementById("Add_button");
const saveButton = document.getElementById("Save_button");
const taskList = document.getElementById("taskList");
const tagInput = document.getElementById("task_tag");
const saveMessage = document.getElementById("save-message");

// Update the display title as the user types
titleInput.addEventListener("input", () => {
  displayTitle.textContent = titleInput.value.trim() || "Untitled";
});

// Add a new task
addButton.addEventListener("click", () => {
  const text = taskInput.value.trim();
  const tag = tagInput.value.trim();

  if (text !== "") {
    const task = {
      text: text,
      tag: tag,
      id: Date.now()
    };
    tasks.push(task);
    renderTask(task);
    taskInput.value = "";
    tagInput.value = "";
  }
});

// Render a task in the list
function renderTask(task) {
  const li = document.createElement("li");

  const taskText = document.createElement("span");
  taskText.textContent = task.text;

  li.appendChild(taskText);

  // Tag badge
  if (task.tag) {
    const tagBadge = document.createElement("span");
    tagBadge.textContent = task.tag;
    tagBadge.classList.add("task-tag");
    li.appendChild(tagBadge);
  }

  li.dataset.id = task.id;

  const deleteIcon = document.createElement("img");
  deleteIcon.src = "/static/icons/delete_icon.png";
  deleteIcon.alt = "Delete";
  deleteIcon.classList.add("delete-icon");
  deleteIcon.style.cursor = "pointer";
  deleteIcon.style.marginLeft = "10px";
  deleteIcon.addEventListener("click", () => deleteTask(task.id, li));

  li.appendChild(deleteIcon);
  taskList.appendChild(li);
}


// Delete a task
function deleteTask(id, element) {
  tasks = tasks.filter(task => task.id !== id);
  taskList.removeChild(element);
}

// Show a save message on the page
function showSaveMessage(message, isError = false) {
  saveMessage.textContent = message;
  saveMessage.className = "save-message" + (isError ? " error" : "");
  setTimeout(() => {
    saveMessage.textContent = "";
    saveMessage.className = "save-message";
  }, 3000);
}

// Save tasks handler
saveButton.addEventListener("click", () => {
  fetch("/save_tasks", { // <-- FIXED ROUTE
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
    title: titleInput.value || "Untitled",
    tasks: tasks.map(t => ({ text: t.text, tag: t.tag }))
  })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success !== false) {
        showSaveMessage(data.message || "Tasks saved!");
      } else {
        showSaveMessage(data.message || "Failed to save tasks.", true);
      }
    })
    .catch(error => {
      console.error("Error saving tasks:", error);
      showSaveMessage("Failed to save tasks.", true);
    });
});
