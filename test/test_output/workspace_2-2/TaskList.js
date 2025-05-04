import React, { useEffect } from 'react';
import { Draggable } from 'react-beautiful-dnd';

export default function TaskList({ tasks, deleteTask, updateTask, setEditingTask }) {
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Delete') {
        const selectedTask = document.activeElement.closest('.task-item');
        if (selectedTask) {
          const taskId = parseInt(selectedTask.getAttribute('data-id'), 10);
          deleteTask(taskId);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [deleteTask]);

  return (
    <div className="task-list">
      {tasks.map((task, index) => (
        <Draggable key={task.id} draggableId={task.id.toString()} index={index}>
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.draggableProps}
              {...provided.dragHandleProps}
              className={`task-item ${task.completed ? 'completed' : ''}`}
              data-id={task.id}
              tabIndex={0}
            >
              <div className="task-details">
                <h3>{task.title}</h3>
                <p>{task.description}</p>
                <span className="category">{task.category}</span>
              </div>
              <div className="task-actions">
                <button
                  onClick={() => updateTask(task.id, { completed: !task.completed })}
                  aria-label={task.completed ? 'Undo completion' : 'Mark as complete'}
                >
                  {task.completed ? 'Undo' : 'Complete'}
                </button>
                <button onClick={() => setEditingTask(task)} aria-label="Edit task">
                  Edit
                </button>
                <button onClick={() => deleteTask(task.id)} aria-label="Delete task">
                  Delete
                </button>
              </div>
            </div>
          )}
        </Draggable>
      )}
    </div>
  );
}