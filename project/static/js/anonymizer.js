document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const instructions = document.getElementById('instructions');

    startButton.addEventListener('click', () => {
        instructions.textContent = 'Starting camera...';
        startButton.disabled = true;
        
        fetch('/anonymizer/start_camera').then(() => {
            instructions.textContent = 'Live feed active. Faces will be blurred.';
            stopButton.disabled = false;
        });
    });

    stopButton.addEventListener('click', () => {
        instructions.textContent = 'Camera is off. Press "Start Camera" to begin.';
        stopButton.disabled = true;
        startButton.disabled = false;
        fetch('/anonymizer/stop_camera');
    });
});