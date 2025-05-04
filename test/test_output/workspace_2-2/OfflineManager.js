const OfflineManager = {
  // Save tasks to local storage
  saveTasks: (tasks) => {
    localStorage.setItem('tasks', JSON.stringify(tasks));
  },

  // Load tasks from local storage
  loadTasks: () => {
    const tasks = localStorage.getItem('tasks');
    return tasks ? JSON.parse(tasks) : [];
  },

  // Clear locally stored tasks
  clearLocalTasks: () => {
    localStorage.removeItem('tasks');
  },

  // Resolve conflicts between local and server tasks
  resolveConflict: (localTask, serverTask) => {
    return new Date(localTask.last_updated) > new Date(serverTask.last_updated)
      ? localTask
      : serverTask;
  },
};

export default OfflineManager;