#!/bin/bash
echo "Starting AI Shopping Assistant MVP..."
echo ""
echo "Starting Mock E-commerce APIs..."
python mock_apis.py &
MOCK_PID=$!
sleep 3
echo ""
echo "Starting Shopping Assistant Web Interface..."
python web_interface.py &
WEB_PID=$!
sleep 3
echo ""
echo "Opening web interface..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8016
elif command -v open &> /dev/null; then
    open http://localhost:8016
fi
echo ""
echo "Shopping Assistant is starting up!"
echo "Mock APIs: http://localhost:8015"
echo "Web Interface: http://localhost:8016"
echo ""
echo "Press Ctrl+C to stop all services"
trap "kill $MOCK_PID $WEB_PID; exit" INT
wait
