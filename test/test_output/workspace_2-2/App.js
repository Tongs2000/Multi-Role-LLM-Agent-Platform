import React, { useState, useEffect, useCallback } from 'react';
import { DragDropContext, Droppable } from 'react-beautiful-dnd';
import TaskList from './TaskList';
import TaskForm from './TaskForm';
import ProgressIndicator from './ProgressIndicator';
import OfflineManager from './OfflineManager';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filter, setFilter] = useState('all');
  const [notification, setNotification] = useState(null);
  const [editingTask, setEditingTask] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Check connectivity
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Fetch tasks and categories
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tasksResponse, categoriesResponse] = await Promise.all([
          fetch('/api/tasks'),
          fetch('/api/categories'),
        ]);
        const tasksData = await tasksResponse.json();
        const categoriesData = await categoriesResponse.json();
        setTasks(tasksData);
        setCategories(categoriesData);
      } catch (error) {
        console.error('Error fetching data:', error);
        if (!isOnline) {
          const localTasks = OfflineManager.loadTasks();
          setTasks(localTasks);
        }
      }
    };
    fetchData();
  }, [isOnline]);

  // Filter tasks
  const filteredTasks = filter === 'all' ? tasks : tasks.filter((task) => task.category === filter);

  // Calculate completion progress
  const progress = tasks.length > 0 ? (tasks.filter((task) => task.completed).length / tasks.length) * 100 : 0;

  // Handle drag-and-drop reordering
  const handleDragEnd = (result) => {
    if (!result.destination) return;
    const reorderedTasks = Array.from(tasks);
    const [movedTask] = reorderedTasks.splice(result.source.index, 1);
    reorderedTasks.splice(result.destination.index, 0, movedTask);
    setTasks(reorderedTasks);
    OfflineManager.saveTasks(reorderedTasks);
  };

  // CRUD operations with offline support
  const addTask = useCallback(async (task) => {
    try {
      if (isOnline) {
        const response = await fetch('/api/tasks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(task),
        });
        const newTask = await response.json();
        setTasks((prev) => [...prev, newTask]);
        setNotification({ type: 'success', message: 'Task added!', undo: null });
      } else {
        const newTasks = [...tasks, { ...task, id: Date.now(), local: true }];
        setTasks(newTasks);
        OfflineManager.saveTasks(newTasks);
        setNotification({ type: 'success', message: 'Task added (offline)!', undo: null });
      }
    } catch (error) {
      console.error('Error adding task:', error);
      setNotification({ type: 'error', message: 'Failed to add task.' });
    }
  }, [isOnline, tasks]);

  const deleteTask = useCallback(async (id) => {
    const deletedTask = tasks.find((task) => task.id === id);
    try {
      if (isOnline) {
        await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
        const newTasks = tasks.filter((task) => task.id !== id);
        setTasks(newTasks);
        setNotification({
          type: 'success',
          message: 'Task deleted!',
          undo: () => addTask(deletedTask),
        });
      } else {
        const newTasks = tasks.filter((task) => task.id !== id);
        setTasks(newTasks);
        OfflineManager.saveTasks(newTasks);
        setNotification({
          type: 'success',
          message: 'Task deleted (offline)!',
          undo: () => addTask(deletedTask),
        });
      }
    } catch (error) {
      console.error('Error deleting task:', error);
      setNotification({ type: 'error', message: 'Failed to delete task.' });
    }
  }, [isOnline, tasks, addTask]);

  const updateTask = useCallback(async (id, updates) => {
    try {
      if (isOnline) {
        const response = await fetch(`/api/tasks/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updates),
        });
        const updatedTask = await response.json();
        setTasks((prev) => prev.map((task) => (task.id === id ? updatedTask : task)));
        setNotification({ type: 'success', message: 'Task updated!' });
      } else {
        const newTasks = tasks.map((task) =>
          task.id === id ? { ...task, ...updates } : task
        );
        setTasks(newTasks);
        OfflineManager.saveTasks(newTasks);
        setNotification({ type: 'success', message: 'Task updated (offline)!' });
      }
    } catch (error) {
      console.error('Error updating task:', error);
      setNotification({ type: 'error', message: 'Failed to update task.' });
    }
  }, [isOnline, tasks]);

  // Sync tasks when online
  useEffect(() => {
    if (isOnline) {
      const syncTasks = async () => {
        const localTasks = OfflineManager.loadTasks().filter((task) => task.local);
        if (localTasks.length > 0) {
          try {
            await fetch('/api/tasks/sync', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(localTasks),
            });
            OfflineManager.clearLocalTasks();
            const response = await fetch('/api/tasks');
            const updatedTasks = await response.json();
            setTasks(updatedTasks);
          } catch (error) {
            console.error('Error syncing tasks:', error);
          }
        }
      };
      syncTasks();
    }
  }, [isOnline]);

  return (
    <div className="App">
      <h1>Todo List {!isOnline && '(Offline)'}</h1>
      <ProgressIndicator progress={progress} />
      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.message}
          {notification.undo && (
            <button onClick={notification.undo} className="undo-button">
              Undo
            </button>
          )}
        </div>
      )}
      <TaskForm
        addTask={addTask}
        categories={categories}
        editingTask={editingTask}
        updateTask={updateTask}
        setEditingTask={setEditingTask}
      />
      <div className="filter">
        <label>Filter by category:</label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All</option>
          {categories.map((category) => (
            <option key={category.id} value={category.name}>
              {category.name}
            </option>
          ))}
        </select>
      </div>
      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="tasks">
          {(provided) => (
            <div ref={provided.innerRef} {...provided.droppableProps}>
              <TaskList
                tasks={filteredTasks}
                deleteTask={deleteTask}
                updateTask={updateTask}
                setEditingTask={setEditingTask}
              />
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>
    </div>
  );
}

export default App;