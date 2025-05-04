#!/bin/bash

# Install backend dependencies
cd backend && python -m pip install -r requirements.txt &

# Install frontend dependencies
cd ../frontend && npm install &

# Wait for installations to complete
wait

# Run backend and frontend in parallel
cd ../backend && python app.py &
cd ../frontend && npm start &

# Wait for both processes to complete (they won't, but this keeps them running)
wait

cat > run_app.sh << 'EOF'
#!/bin/bash

# Install backend dependencies
cd backend && python -m pip install -r requirements.txt &

# Install frontend dependencies
cd ../frontend && npm install &

# Wait for installations to complete
wait

# Run backend and frontend in parallel
cd ../backend && python app.py &
cd ../frontend && npm start &

# Wait for both processes to complete (they won't, but this keeps them running)
wait
EOF

chmod +x run_app.sh
./run_app.sh
