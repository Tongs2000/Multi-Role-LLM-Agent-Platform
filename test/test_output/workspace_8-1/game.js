const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game variables
let snake = [{ x: 200, y: 200 }];
let food = { x: 0, y: 0 };
let direction = 'RIGHT';
let gameOver = false;
let score = 0;

// Initialize the game
function init() {
    generateFood();
    document.addEventListener('keydown', changeDirection);
    gameLoop();
}

// Main game loop
function gameLoop() {
    if (gameOver) {
        alert(`Game Over! Score: ${score}`);
        document.location.reload();
        return;
    }

    setTimeout(() => {
        clearCanvas();
        drawFood();
        moveSnake();
        drawSnake();
        checkCollision();
        gameLoop();
    }, 100);
}

// Clear the canvas
function clearCanvas() {
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

// Draw the snake
function drawSnake() {
    snake.forEach(segment => {
        ctx.fillStyle = 'green';
        ctx.fillRect(segment.x, segment.y, 20, 20);
    });
}

// Draw the food
function drawFood() {
    ctx.fillStyle = 'red';
    ctx.fillRect(food.x, food.y, 20, 20);
}

// Generate food at random positions
function generateFood() {
    food.x = Math.floor(Math.random() * 20) * 20;
    food.y = Math.floor(Math.random() * 20) * 20;
}

// Change snake direction based on keyboard input
function changeDirection(event) {
    const key = event.keyCode;
    if (key === 37 && direction !== 'RIGHT') direction = 'LEFT';
    else if (key === 38 && direction !== 'DOWN') direction = 'UP';
    else if (key === 39 && direction !== 'LEFT') direction = 'RIGHT';
    else if (key === 40 && direction !== 'UP') direction = 'DOWN';
}

// Move the snake
function moveSnake() {
    const head = { ...snake[0] };

    switch (direction) {
        case 'LEFT': head.x -= 20; break;
        case 'UP': head.y -= 20; break;
        case 'RIGHT': head.x += 20; break;
        case 'DOWN': head.y += 20; break;
    }

    snake.unshift(head);

    // Check if snake ate the food
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        generateFood();
    } else {
        snake.pop();
    }
}

// Check for collisions
function checkCollision() {
    const head = snake[0];

    // Wall collision
    if (head.x < 0 || head.x >= canvas.width || head.y < 0 || head.y >= canvas.height) {
        gameOver = true;
    }

    // Self collision
    for (let i = 1; i < snake.length; i++) {
        if (head.x === snake[i].x && head.y === snake[i].y) {
            gameOver = true;
        }
    }
}

// Save score to backend
function saveScore(score) {
    fetch('http://localhost:3000/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player: 'Player', score })
    }).catch(err => console.error('Error saving score:', err));
}

// Fetch and display high scores
function fetchHighScores() {
    fetch('http://localhost:3000/scores')
        .then(res => res.json())
        .then(scores => {
            const scoresList = document.getElementById('scoresList');
            scoresList.innerHTML = '';
            scores.sort((a, b) => b.score - a.score).slice(0, 5).forEach(score => {
                const li = document.createElement('li');
                li.textContent = `${score.player}: ${score.score}`;
                scoresList.appendChild(li);
            });
        })
        .catch(err => console.error('Error fetching scores:', err));
}

// Start the game
init();

// Example: Fetch high scores on startup
fetchHighScores();