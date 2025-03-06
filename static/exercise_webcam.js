// exercise_webcam.js
navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
        const webcamElement = document.getElementById("webcam");
        if (webcamElement) {
            webcamElement.srcObject = stream;
        }
    })
    .catch((error) => {
        console.error("Error accessing the webcam:", error);
    });
