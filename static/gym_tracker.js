// Define the quit button
const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');
const startButton = document.getElementById("start_button");
const quitButton = document.getElementById("quit_button");

const repOutput = document.getElementById("rep_count");
const visOutput = document.getElementById("visibility");
const stageOutput = document.getElementById("stage");
const timerElement = document.getElementById("timer");

let visible = true,
    stage = 'down',
    counter = 0,
    target_count = -1;

function onResults(results) {
    if (!results.poseLandmarks) return;

    landmarks = results.poseLandmarks;

    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

    canvasCtx.globalCompositeOperation = 'destination-atop';
    canvasCtx.drawImage(
        results.image, 0, 0, canvasElement.width, canvasElement.height);

    canvasCtx.globalCompositeOperation = 'source-over';
    
    drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
        {color: '#00FF00', lineWidth: 4});
    drawLandmarks(canvasCtx, results.poseLandmarks,
       {color: '#FF0000', lineWidth: 2});

    // angle calculations

    const calculateAngle = (a, b, c) => {
        a = Array.isArray(a) ? a : [a[0], a[1]];
        b = Array.isArray(b) ? b : [b[0], b[1]];
        c = Array.isArray(c) ? c : [c[0], c[1]];

        const radians = Math.atan2(c[1] - b[1], c[0] - b[0]) - Math.atan2(a[1] - b[1], a[0] - b[0]);
        let angle = Math.abs((radians * 180.0) / Math.PI);

        if (angle > 180.0) {
            angle = 360 - angle;
        }

        return angle;

        
    }

    const LEFT_SHOULDER = 11,
        LEFT_ELBOW = 13,
        LEFT_WRIST = 15,
        VISIBILITY_THRESHOLD = 0.5;

    if (landmarks[LEFT_SHOULDER]['visibility'] < VISIBILITY_THRESHOLD ||
        landmarks[LEFT_ELBOW]['visibility'] < VISIBILITY_THRESHOLD ||
        landmarks[LEFT_WRIST]['visibility'] < VISIBILITY_THRESHOLD) {
        visible = false;
    } else {
        visible = true;
        shoulder = [landmarks[LEFT_SHOULDER].x, landmarks[LEFT_SHOULDER].y];
        elbow = [landmarks[LEFT_ELBOW].x, landmarks[LEFT_ELBOW].y];
        wrist = [landmarks[LEFT_WRIST].x, landmarks[LEFT_WRIST].y];

        angle = calculateAngle(shoulder, elbow, wrist);
        console.log(angle)

        if (angle > 160 && stage == "up") {
            stage = "down";
        } else if (angle < 60 && stage == "down") {
            stage = "up";
            counter++;
        }

        if (counter == target_count) {
            stopTimer()
            camera.stop()
        }
        repOutput.innerHTML = `rep count : ${counter}`;
        stageOutput.innerHTML = `stage : ${stage}`;
    }
    visOutput.innerHTML = `visible : ${visible}`;

    canvasCtx.restore();
}

const pose = new Pose({ locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
}});
pose.setOptions({
    modelComplexity: 1,
    smoothLandmarks: true,
    enableSegmentation: true,
    smoothSegmentation: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});
pose.onResults(onResults);

const camera = new Camera(videoElement, {
    onFrame: async () => {
        await pose.send({ image: videoElement });
    },
    width: 1280,
    height: 720,
});
camera.start();
startButton.onclick = () => {
    target_count = document.getElementById("target_count").value;
    visible = true;
    stage = 'down';
    counter = 0;
    //camera.start();
    startTimer();
}

let seconds = 0;
let timerInterval;

function stopTimer() {
    console.log(seconds)
    fetch("http://127.0.0.1:5000/exercise_bicep_curls", {
        method: "POST",
        body: JSON.stringify({
            time: seconds,
            rep_count : counter
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });
    clearInterval(timerInterval);
}

function startTimer() {
    resetTimer();
    timerInterval = setInterval(() => {
        seconds++;
        displayTime();
    }, 1000);
}

function resetTimer() {
    stopTimer();
    seconds = 0;
    displayTime();
}

function displayTime() {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    timerElement.textContent = `time : ${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
}

// Additional functions
async function sendExerciseDataToServer() {
    try {
        const response = await fetch("http://127.0.0.1:5000/exercise_data", {
            method: "POST",
            body: JSON.stringify({
                time: seconds,
                rep_count: counter,
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
            },
        });

        if (response.ok) {
            const responseData = await response.json();
            return { success: responseData.success };
        } else {
            return { success: false };
        }
    } catch (error) {
        console.error("Error sending exercise data:", error);
        return { success: false };
    }
}
quitButton.onclick = () => {
    const confirmQuit = confirm("Do you want to check the dashboard?");

    if (confirmQuit) {
        sendExerciseDataToServer().then(response => {
            if (response.success) {
                alert("Exercise data has been successfully stored.");
                window.location.href = "/dashboard"; // Redirect to the dashboard page
            } else {
                alert("Failed to store exercise data. Please try again.");
            }
            stopExerciseTracking();
        });
    } else {
        window.location.href = "/customized_exercises"; // Redirect to the customized exercises page

    }
};

