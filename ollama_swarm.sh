PORTS=(11435 11436 11437 11438 11439 11440 11441 11442 )
 
for PORT in "${PORTS[@]}"
do
  echo "Starting Ollama server on port $PORT..."
  OLLAMA_HOST="localhost:$PORT" ollama serve &
done
 
# Wait for the servers to start
wait