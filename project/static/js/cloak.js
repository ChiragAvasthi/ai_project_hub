document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const recaptureButton = document.getElementById('recaptureButton');
    const colorPalette = document.getElementById('color-palette');
    const instructions = document.getElementById('instructions');

    function showCountdown(callback) {
        let countdown = 5;
        instructions.textContent = `Clear the scene! Capturing background in ${countdown}...`;
        const interval = setInterval(() => {
            countdown--;
            if (countdown > 0) {
                instructions.textContent = `Clear the scene! Capturing background in ${countdown}...`;
            } else {
                clearInterval(interval);
                if (callback) callback();
            }
        }, 1000);
    }

    startButton.addEventListener('click', () => {
        instructions.textContent = 'Starting camera... Please wait.';
        startButton.disabled = true;

        fetch('/cloak/start_camera').then(() => {
            showCountdown(() => {
                instructions.textContent = 'Background captured! Use your cloak.';
                stopButton.disabled = false;
                recaptureButton.disabled = false;
            });
        });
    });

    stopButton.addEventListener('click', () => {
        instructions.textContent = 'Camera is off. Press "Start Camera" to begin.';
        stopButton.disabled = true;
        recaptureButton.disabled = true;
        startButton.disabled = false;
        fetch('/cloak/stop_camera');
    });

    recaptureButton.addEventListener('click', () => {
        startButton.disabled = true;
        stopButton.disabled = true;
        recaptureButton.disabled = true;
        
        fetch('/cloak/recapture_background').then(() => {
            showCountdown(() => {
                instructions.textContent = 'Background recaptured!';
                stopButton.disabled = false;
                recaptureButton.disabled = false;
            });
        });
    });

    colorPalette.addEventListener('click', (e) => {
        if (e.target.classList.contains('color-swatch')) {
            const selectedColor = e.target.dataset.color;
            if (!e.target.classList.contains('active')) {
                document.querySelector('.color-swatch.active').classList.remove('active');
                e.target.classList.add('active');
                fetch(`/cloak/set_color/${selectedColor}`);
            }
        }
    });
});