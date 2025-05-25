document.addEventListener("DOMContentLoaded", () => {
  const listId = document.getElementById("task-list").dataset.listId;
  const taskList = document.getElementById("task-list");
  const completedCountDisplay = document.getElementById("completed-count");

  function updateCompletedCount() {
    const checkboxes = taskList.querySelectorAll("input[type='checkbox']");
    const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
    completedCountDisplay.textContent = `✔️ ${checkedCount} / ${checkboxes.length} tasks completed`;
  }

  taskList.querySelectorAll("input[type='checkbox']").forEach((checkbox, index) => {
    checkbox.addEventListener("change", () => {
      const li = checkbox.closest("li");
      const text = li.querySelector("span").textContent;
      const done = checkbox.checked;

      li.querySelector("span").classList.toggle("done", done);
      updateCompletedCount();

      fetch(`/update_task/${listId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index, done })
      });
    });
  });

  document.getElementById("delete-list").addEventListener("click", () => {
    if (confirm("Are you sure you want to delete this list?")) {
      fetch(`/delete_list/${listId}`, {
        method: "POST"
      }).then(() => window.location.href = "/saved_lists");
    }
  });

  updateCompletedCount();

  // Enable drag-and-drop sorting using SortableJS
  const script = document.createElement('script');
  script.src = "https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js";
  script.onload = () => {
    new Sortable(taskList, {
      animation: 150,
      onEnd: () => {
        // After sorting, send updated order to server
        const tasks = [];
        taskList.querySelectorAll("li").forEach(li => {
          const text = li.querySelector("span").textContent;
          const done = li.querySelector("input").checked;
          tasks.push({ text, done });
        });

        fetch(`/reorder_tasks/${listId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tasks })
        });
      }
    });
  };
  document.body.appendChild(script);
});
