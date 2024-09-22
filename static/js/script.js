document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const resultDiv = document.getElementById('result');

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
                } else {
                    resultDiv.innerHTML = `
                        <p>Resume uploaded and parsed successfully!</p>
                        <a href="/resume/${data.resume_id}">View Parsed Resume</a>
                    `;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                resultDiv.innerHTML = '<p class="error">An error occurred while uploading the resume.</p>';
            });
        });
    }
});