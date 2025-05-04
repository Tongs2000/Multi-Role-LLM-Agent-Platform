import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Calculator.css';

const Calculator = () => {
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [activeButton, setActiveButton] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const handleButtonClick = (value) => {
    setError('');
    if (value === '=') {
      calculateResult();
    } else if (value === 'C') {
      clearAll();
    } else if (value === '⌫') {
      setInput(prev => prev.slice(0, -1));
    } else {
      setInput(prev => prev + value);
    }
  };

  const calculateResult = async () => {
    try {
      const response = await axios.post(`${API_URL}/calculate`, {
        expression: input
      });
      setResult(response.data.result.toString());
      setInput(response.data.result.toString());
    } catch (err) {
      setError(err.response?.data?.error || 'Calculation error');
    }
  };

  const clearAll = () => {
    setInput('');
    setResult('');
    setError('');
  };

  const handleKeyDown = (e) => {
    const key = e.key;
    const buttonMap = {
      '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
      '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
      '+': '+', '-': '-', '*': '*', '/': '/',
      '(': '(', ')': ')', '.': '.',
      'Enter': '=', 'Escape': 'C', 'Backspace': '⌫'
    };

    if (buttonMap[key]) {
      e.preventDefault();
      setActiveButton(buttonMap[key]);
      setTimeout(() => setActiveButton(null), 100);
      handleButtonClick(buttonMap[key]);
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [input]);

  const buttons = [
    'C', '⌫', '(', ')',
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    '0', '.', '=', '+'
  ];

  return (
    <div className="calculator">
      <h1>Calculator</h1>
      <div className="display">
        <div className="input">{input || '0'}</div>
        <div className="result">{result}</div>
        {error && <div className="error">{error}</div>}
      </div>
      <div className="buttons">
        {buttons.map((btn) => (
          <button
            key={btn}
            onClick={() => handleButtonClick(btn)}
            className={`${activeButton === btn ? 'active' : ''} ${btn === '=' ? 'equals' : ''}`}
          >
            {btn}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Calculator;