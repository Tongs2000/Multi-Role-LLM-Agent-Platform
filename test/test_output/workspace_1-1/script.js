let currentDisplay = '0';
let firstOperand = null;
let operator = null;
let waitingForSecondOperand = false;

const display = document.getElementById('display');

function updateDisplay() {
    display.textContent = currentDisplay;
}

function appendToDisplay(value) {
    if (waitingForSecondOperand) {
        currentDisplay = value;
        waitingForSecondOperand = false;
    } else {
        currentDisplay = currentDisplay === '0' ? value : currentDisplay + value;
    }
    updateDisplay();
}

function clearDisplay() {
    currentDisplay = '0';
    firstOperand = null;
    operator = null;
    waitingForSecondOperand = false;
    updateDisplay();
}

function handleOperator(nextOperator) {
    const inputValue = parseFloat(currentDisplay);

    if (operator && waitingForSecondOperand) {
        operator = nextOperator;
        return;
    }

    if (firstOperand === null) {
        firstOperand = inputValue;
    } else if (operator) {
        const result = calculate(firstOperand, inputValue, operator);
        currentDisplay = `${result}`;
        firstOperand = result;
        updateDisplay();
    }

    waitingForSecondOperand = true;
    operator = nextOperator;
}

function calculate() {
    const inputValue = parseFloat(currentDisplay);

    if (operator === '/' && inputValue === 0) {
        alert('Error: Division by zero');
        clearDisplay();
        return;
    }

    if (firstOperand === null || operator === null) {
        return;
    }

    const result = calculate(firstOperand, inputValue, operator);
    currentDisplay = `${result}`;
    firstOperand = null;
    operator = null;
    waitingForSecondOperand = false;
    updateDisplay();
}

function calculate(firstOperand, secondOperand, operator) {
    switch (operator) {
        case '+':
            return firstOperand + secondOperand;
        case '-':
            return firstOperand - secondOperand;
        case '*':
            return firstOperand * secondOperand;
        case '/':
            return firstOperand / secondOperand;
        default:
            return secondOperand;
    }
}

// Keyboard support
document.addEventListener('keydown', (event) => {
    const key = event.key;

    if (/[0-9]/.test(key)) {
        appendToDisplay(key);
    } else if (['+', '-', '*', '/'].includes(key)) {
        handleOperator(key);
    } else if (key === 'Enter') {
        calculate();
    } else if (key === 'Escape') {
        clearDisplay();
    }
});