document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');

    // Make the drop zone clickable to open the file dialog
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Automatically submit the form when a file is selected via the dialog
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            uploadForm.submit();
        }
    });

    // Add visual feedback when a file is dragged over the zone
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault(); // Prevent browser's default behavior
        dropZone.classList.add('drag-over');
    });

    // Remove visual feedback when the file leaves the zone
    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, () => {
            dropZone.classList.remove('drag-over');
        });
    });

    // Handle the dropped file
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault(); // Prevent browser's default behavior
        dropZone.classList.remove('drag-over');

        // Check if files were dropped
        if (e.dataTransfer.files.length > 0) {
            // Assign the dropped files to our hidden file input
            fileInput.files = e.dataTransfer.files;
            
            // Automatically submit the form
            uploadForm.submit();
        }
    });
});