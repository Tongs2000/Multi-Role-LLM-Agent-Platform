let currentInput = '0';
let previousInput = '';
let operation = null;
let resetScreen = false;

const display = document.getElementById('display');

function updateDisplay() {
    display.textContent = currentInput;
}

function appendToDisplay(value) {
    if (currentInput === '0' || resetScreen) {
        currentInput = '';
        resetScreen = false;
    }
    currentInput += value;
    updateDisplay();
}

function clearDisplay() {
    currentInput = '0';
    previousInput = '';
    operation = null;
    updateDisplay();
}

function clearEntry() {
    currentInput = '0';
    updateDisplay();
}

function chooseOperation(op) {
    if (currentInput === '') return;
    if (previousInput !== '') {
        calculate();
    }
    operation = op;
    previousInput = currentInput;
    resetScreen = true;
}

function calculate() {
    let result;
    const prev = parseFloat(previousInput);
    const current = parseFloat(currentInput);

    if (isNaN(prev) || isNaN(current)) return;

    switch (operation) {
        case '+':
            result = prev + current;
            break;
        case '-':
            result = prev - current;
            break;
        case '*':
            result = prev * current;
            break;
        case '/':
            if (current === 0) {
                alert('Error: Division by zero');
                clearDisplay();
                return;
            }
            result = prev / current;
            break;
        case '%':
            result = prev % current;
            break;
        default:
            return;
    }

    currentInput = result.toString();
    operation = null;
    previousInput = '';
    resetScreen = true;
    updateDisplay();
}

// Keyboard support
document.addEventListener('keydown', (e) => {
    if (e.key >= '0' && e.key <= '9') appendToDisplay(e.key);
    else if (e.key === '.') appendToDisplay('.');
    else if (e.key === '+' || e.key === '-' || e.key === '*' || e.key === '/') chooseOperation(e.key);
    else if (e.key === 'Enter' || e.key === '=') calculate();
    else if (e.key === 'Escape') clearDisplay();
    else if (e.key === 'Backspace') {
        currentInput = currentInput.slice(0, -1) || '0';
        updateDisplay();
    }
});

// Initialize display
updateDisplay();