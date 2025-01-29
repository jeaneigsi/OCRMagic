const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const imagePreview = document.getElementById('imagePreview');
const textPreview = document.getElementById('textPreview');
const submitBtn = document.getElementById('submitBtn');
const enhanceBtn = document.getElementById('enhanceBtn');
const glassmorphism = document.getElementById('glassmorphism');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const urlPrefixInput = document.getElementById('urlPrefixInput');
const authTokenInput = document.getElementById('authTokenInput');
const tutorialPopup = document.getElementById('tutorialPopup');
const fileList = document.getElementById('fileList');
const uploadControls = document.getElementById('uploadControls');
const clearAllBtn = document.getElementById('clearAllBtn');
const convertBtn = document.getElementById('convertBtn');
const resultArea = document.getElementById('resultArea');
const resultList = document.getElementById('resultList');
const fileCountElement = document.getElementById('fileCount');
const startOverBtn = document.getElementById('startOverBtn');
const downloadAllBtn = document.getElementById('downloadAllBtn');
const getApiButtons = document.querySelectorAll('.get-api-btn');
const textModal = document.getElementById('textModal');
const textModalContent = document.getElementById('textModalContent');
const closeModalButton = document.getElementById('closeModal')


let currentImageIndex = 0;
let uploadedImages = [];
let extractedTexts = [];
// Automatically construct the URL prefix
const urlPrefix = window.location.origin;

function showTutorial() {
    if (tutorialPopup) {
        tutorialPopup.style.display = 'block';
    }
}

getApiButtons.forEach(button => {
    button.addEventListener('click', () => {
       window.location.href = '/pricing'; // Redirect to the /pricing endpoint
     });
  });

function closeTutorial() {
    if (tutorialPopup) {
        tutorialPopup.style.display = 'none';
    }
}

if (uploadArea) {
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        handleFiles(e.dataTransfer.files);
    });
}

if (fileInput) {
    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
    });
}

function handleFiles(files) {
    uploadedImages = Array.from(files);
    extractedTexts = new Array(uploadedImages.length).fill('');
    currentImageIndex = 0;
    fileList.innerHTML = '';

    if (uploadedImages.length > 0) {
        uploadControls.style.display = 'flex';
        uploadedImages.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.classList.add('file-item');
            fileItem.innerHTML = `
                <span>${file.name}</span>
                 <button class="remove-file-btn" data-index="${index}">
                      <i class="fas fa-times"></i>
                 </button>
           `;
            fileList.appendChild(fileItem);
        });
        const removeFileButtons = document.querySelectorAll('.remove-file-btn');

        removeFileButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const fileIndex = parseInt(event.target.dataset.index);
                uploadedImages = uploadedImages.filter((_, index) => index !== fileIndex);
                extractedTexts = extractedTexts.filter((_, index) => index !== fileIndex)
                handleFiles(uploadedImages);
            });
        });
        fileCountElement.innerText = `(${uploadedImages.length})`;
    } else {
        uploadControls.style.display = 'none';
        fileCountElement.innerText = '';
    }
    resultArea.style.display = 'none';
    resultList.innerHTML = '';
    updateSliderControls();
}


function updateSliderControls() {
    if (prevBtn && nextBtn) {
        prevBtn.disabled = currentImageIndex === 0;
        nextBtn.disabled = currentImageIndex === uploadedImages.length - 1;
    }
}

if (clearAllBtn) {
    clearAllBtn.addEventListener('click', () => {
        uploadedImages = [];
        extractedTexts = []
        handleFiles([])
    })
}

if (prevBtn) {
    prevBtn.addEventListener('click', () => {
        if (currentImageIndex > 0) {
            currentImageIndex--;
            updateTextPreview();
        }
    });
}
if (nextBtn) {
    nextBtn.addEventListener('click', () => {
        if (currentImageIndex < uploadedImages.length - 1) {
            currentImageIndex++;
             updateTextPreview();
        }
    });
}

if (enhanceBtn) {
    enhanceBtn.addEventListener('click', () => {
        if (glassmorphism) {
            glassmorphism.classList.add('active');
            setTimeout(() => {
                extractedTexts[currentImageIndex] = 'Enhanced text result for image ' + (currentImageIndex + 1);
                updateTextPreview();
                glassmorphism.classList.remove('active');
            }, 2000);
        }
    });
}
function openTextModal(text) {
    textModalContent.innerText = text;
    textModal.style.display = 'block';
}

function closeTextModal() {
    textModal.style.display = 'none';
}
function updateResultArea() {
    resultList.innerHTML = '';
  uploadedImages.forEach((file, index) => {
      const resultItem = document.createElement('div');
      resultItem.classList.add('result-item');
      resultItem.innerHTML = `
          <div class="image-preview">
             <img src="${URL.createObjectURL(file)}">
           </div>
          <div class="progress-bar-container">
              <div class="progress-bar" id="progressBar-${index}"></div>
          </div>
          <div class="action-controls">
              <button class="view-text-btn"  data-index="${index}">View</button>
              <button class="download-btn" data-index="${index}" style="display:none">Download</button>
           </div>
    `

     resultList.appendChild(resultItem);
    });
}
if (convertBtn) {
    convertBtn.addEventListener('click', async () => {
        if (glassmorphism) {
            glassmorphism.classList.add('active');
        }
        resultArea.style.display = 'block';
        updateResultArea();
        try {
            for (let i = 0; i < uploadedImages.length; i++) {
                const imageFile = uploadedImages[i];
                const formData = new FormData();
                formData.append('file', imageFile);
                const progressBar = document.getElementById(`progressBar-${i}`);
                const downloadButton = document.querySelector(`.download-btn[data-index="${i}"]`)
                let fetchUrl = `${urlPrefix}/api/v1/paddle-ocr/ocr`;

                const response = await fetch(fetchUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        "accept": "application/json"
                    }
                });

                if (!response.ok) {
                    throw new Error('Error during text extraction for image ' + (i + 1));
                }
                const result = await response.json();
                const extractedText = result.rec_text || 'No text extracted';
                extractedTexts[i] = extractedText;
                let progress = 0;
                const interval = setInterval(() => {
                    progress += 20;
                    progressBar.style.width = `${progress}%`;
                    if (progress >= 100) {
                        clearInterval(interval);
                        downloadButton.style.display = 'inline-block'
                    }
                }, 100);
            }
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            if (glassmorphism) {
                glassmorphism.classList.remove('active');
            }
            const viewTextButtons = document.querySelectorAll('.view-text-btn');
            viewTextButtons.forEach(button => {
                button.addEventListener('click', (event) => {
                   const index = parseInt(event.target.dataset.index);
                    openTextModal(extractedTexts[index])
                });
            });
            const downloadButtons = document.querySelectorAll('.download-btn');
            downloadButtons.forEach(button => {
                button.addEventListener('click', async (event) => {
                    const index = parseInt(event.target.dataset.index);
                    const imageFile = uploadedImages[index];
                    const extractedText = extractedTexts[index]
                    const blob = new Blob([extractedText], { type: "text/plain" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `text_result_${imageFile.name.split('.').slice(0, -1).join('.')}.txt`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                });
            });
        }
    });
}
function updateTextPreview() {
   if (textPreview) {
       textPreview.innerText = extractedTexts[currentImageIndex];
    }
}

if (startOverBtn) {
    startOverBtn.addEventListener('click', () => {
         uploadedImages = [];
        extractedTexts = []
        handleFiles([])
    });
}
if(downloadAllBtn){
    downloadAllBtn.addEventListener('click', async () => {
        for (let i = 0; i < uploadedImages.length; i++) {
            const imageFile = uploadedImages[i];
            const extractedText = extractedTexts[i];
            const blob = new Blob([extractedText], { type: "text/plain" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `text_result_${imageFile.name.split('.').slice(0, -1).join('.')}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    });
} 
if(closeModalButton){
    closeModalButton.addEventListener('click', () => {
       closeTextModal()
    });
}