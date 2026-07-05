const canvas = document.getElementById("roiCanvas");
const ctx = canvas.getContext("2d");
const container = document.getElementById("container");

const urlParams = new URLSearchParams(window.location.search);
const currentLabId = urlParams.get('lab_id') || 1; 
console.log(`Configuring Workspace Active ID Pipeline Context: ${currentLabId}`);

const image = new Image();

// Recover local text details
const cachedLabName = sessionStorage.getItem('labName');
const cachedTempImage = sessionStorage.getItem('tempImage');

if (cachedLabName) {
    document.getElementById('mainHeaderTitle').innerText = `${cachedLabName} — ROI Configuration Studio`;
}

// Security assurance gate mapping check sequence redirect boundaries
if (!cachedTempImage) {
    alert("No temporary laboratory environment session context configuration found. Returning to upload configuration panel.");
    window.location.href = "upload.html";
} else {
    image.src = cachedTempImage;
}

// Local storage management context configuration access hooks
function initDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open("LabUploadCacheDB", 1);
        request.onsuccess = (e) => resolve(e.target.result);
        request.onerror = (e) => reject(e.target.error);
    });
}

function getItemIndexedDB(key) {
    return initDB().then(db => {
        return new Promise((resolve, reject) => {
            const tx = db.transaction("assets", "readonly");
            const store = tx.objectStore("assets");
            const request = store.get(key);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    });
}

// Wire step navigate back interaction binding handler logic elements
document.getElementById('backBtn').addEventListener('click', () => {
    window.location.href = "upload.html";
});

// image loading 
image.onload = () => {
    canvas.width = image.width;
    canvas.height = image.height;
    ctx.drawImage(image, 0, 0);
    console.log(canvas.width, canvas.height);
};

let startX;
let startY;
let currentX;
let currentY;
let drawing = false;
let rois = [];

// Detect Mouse Press 
canvas.addEventListener("mousedown", (event) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    startX = (event.clientX - rect.left) * scaleX;
    startY = (event.clientY - rect.top) * scaleY;
    drawing = true;
});

// Detect Dragging 
canvas.addEventListener("mousemove", (event) => {
    if (!drawing) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    currentX = (event.clientX - rect.left) * scaleX;
    currentY = (event.clientY - rect.top) * scaleY;

    redrawAllROIs();
    drawRectangle(startX, startY, currentX, currentY, "red");
});

// Detect Mouse Release 
canvas.addEventListener("mouseup", (event) => {
    if (!drawing) return;
    drawing = false;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    currentX = (event.clientX - rect.left) * scaleX;
    currentY = (event.clientY - rect.top) * scaleY;

    const roiName = prompt("Enter ROI Name:");

    const x = Math.min(startX, currentX);
    const y = Math.min(startY, currentY);
    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);

    if (width < 4 || height < 4) return;

    const roi = {
        id: Date.now(),
        name: roiName || `ROI ${rois.length + 1}`,
        x: x / canvas.width,
        y: y / canvas.height,
        width: width / canvas.width,
        height: height / canvas.height
    };

    rois.push(roi);
    redrawAllROIs();
    updateROIList();
});

// event for loading existing rois for a particular image or lab
window.addEventListener("load", loadROIs);

// Draw Rectangle Function 
function drawRectangle(x1, y1, x2, y2, color, label=""){
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(Math.min(x1, x2), Math.min(y1, y2), Math.abs(x2 - x1), Math.abs(y2 - y1));
    ctx.font = "18px Arial";
    ctx.fillStyle = color;
    ctx.fillText(label, Math.min(x1, x2), Math.min(y1, y2) - 5);
}

// Redraw Function 
function redrawCanvas(){
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0);
}

// Redraw Function for multiple ROI 
function redrawAllROIs(){
    redrawCanvas();
    rois.forEach(roi => {
        const x = roi.x * canvas.width;
        const y = roi.y * canvas.height;
        const width = roi.width * canvas.width;
        const height = roi.height * canvas.height;
        drawRectangle(x, y, x + width, y + height, "red", roi.name);
    });
}

// update the roi list with stylized Tailwind components feed
function updateROIList(){
    const list = document.getElementById("roiList");
    list.innerHTML = "";

    rois.forEach(roi => {
        const li = document.createElement("li");
        li.className = "bg-white p-3 rounded-lg border border-slate-200 shadow-sm flex items-center justify-between group hover:border-slate-300 transition-all text-xs";
        li.innerHTML = `
            <div class="flex flex-col gap-0.5">
                <span class="font-bold text-slate-700">${roi.name}</span>
                <span class="text-[10px] text-slate-400 font-mono">
                    X: ${Math.round(roi.x * canvas.width)}, 
                    Y: ${Math.round(roi.y * canvas.height)}, 
                    W: ${Math.round(roi.width * canvas.width)}, 
                    H: ${Math.round(roi.height * canvas.height)}
                </span>
            </div>
            <button onclick="deleteROI(${roi.id})" class="text-slate-400 hover:text-red-500 p-1 rounded transition-colors font-sans font-medium text-xs">
                Delete
            </button>
        `;
        list.appendChild(li);
    });
}

// function for loading existing rois
async function loadROIs(){
    try{
        const response = await fetch(`http://localhost:5000/api/roi/${currentLabId}`);
        if(!response.ok) return;
        const data = await response.json();
        rois = data;
        redrawAllROIs();
        updateROIList();
    } catch(error){
        console.error(error);
    }
}

// function for deleting a roi
function deleteROI(id){
    rois = rois.filter(roi => roi.id !== id);
    redrawAllROIs();
    updateROIList();
}
window.deleteROI = deleteROI;

// Binding integration target hooks
document.getElementById("saveBtn").addEventListener("click", saveROI);

// Unified Save Function combining text configurations, coordination vectors map array, and raw local file assets binary streams
async function saveROI(){
    if (rois.length === 0) {
        alert("Please set or define at least one valid region coordinate bounding matrix profile box target boundary context first.");
        return;
    }

    const modal = document.getElementById('processingModal');
    const spinner = document.getElementById('statusSpinner');
    const checkmark = document.getElementById('statusCheckmark');
    const title = document.getElementById('modalTitle');
    const desc = document.getElementById('modalDesc');

    // CRITICAL RESET STATE: Ensure spinner is active and checkmark is tucked away initially
    spinner.classList.remove('hidden');
    checkmark.classList.add('hidden');
    title.innerText = "Segmenting Media Feed";
    desc.innerText = "The integrated FFmpeg stream pipeline is currently slicing target source components and applying configurations. Do not close this terminal engine window.";

    // Launch overlay visual blocking indicators panel frame layer context interfaces maps
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    try {
        // Fetch original raw stored assets out from local IndexedDB space
        const videoFileBlob = await getItemIndexedDB("videoBlob");
        const imageFileBlob = await getItemIndexedDB("imageBlob");

        if(!videoFileBlob || !imageFileBlob) {
            throw new Error("Local cached resource asset references references are missing. Restart initialization pipelines process sequence.");
        }

        const formData = new FormData();
        formData.append("name", cachedLabName);
        formData.append("image", imageFileBlob, imageFileBlob.name || "snapshot.png");
        formData.append("video", videoFileBlob, videoFileBlob.name || "source_pipeline.mp4");
        formData.append("rois", JSON.stringify(rois));

        const response = await fetch("http://localhost:5000/api/labs/complete-pipeline", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Server runtime validation execution block rejected target assets parameters structure logs.");
        }

        // Start Polling the status endpoint using the newly generated lab_id
        const targetLabId = result.lab_id;
        
        const pollInterval = setInterval(async () => {
            try {
                const statusResponse = await fetch(`http://localhost:5000/api/labs/pipeline-status/${targetLabId}`);
                const statusResult = await statusResponse.json();

                if (statusResult.status === "completed") {
                    clearInterval(pollInterval); // Stop polling

                    // Unveil confirmation components elements metrics structures logs maps
                    spinner.classList.add('hidden');
                    checkmark.classList.remove('hidden');
                    title.innerText = "Pipeline Encoded Successfully!";
                    desc.innerText = "The video streams have been segmented via background tasks. Returning context to initial portal module...";

                    setTimeout(() => {
                        sessionStorage.clear();
                        indexedDB.deleteDatabase("LabUploadCacheDB");
                        window.location.href = "upload.html"; // Clean redirect path back to upload interface
                    }, 2500);

                } else if (statusResult.status === "failed") {
                    clearInterval(pollInterval);
                    throw new Error(statusResult.error || "FFmpeg encountered an encoding exception.");
                }
                // If status is "processing", do nothing, keeping the spinner rolling on screen
                
            } catch (pollError) {
                clearInterval(pollInterval);
                console.error(pollError);
                alert("Polling synchronization dropped: " + pollError.message);
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }
        }, 2000); // Check status every 2 seconds

    } catch(error){
        console.error(error);
        alert("Unified Processing Engine Exception context error: " + error.message);
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}






































/** 
const canvas = document.getElementById("roiCanvas");
const ctx = canvas.getContext("2d");
const container = document.getElementById("container");



// NEW DYNAMIC INGESTION: READ THE EXTRACTED URL IDENTIFIER CONSTRAINT
// =========================================================================
const urlParams = new URLSearchParams(window.location.search);
// Grabs the ID from the URL string parameter, defaulting to 1 if testing locally
const currentLabId = urlParams.get('lab_id') || 1; 
console.log(`Configuring Workspace Active ID Pipeline Context: ${currentLabId}`);




const image = new Image();


// image path 
image.src = "./images/test_image.png";

// image loading 
image.onload = () => {

    canvas.width = image.width;
    canvas.height = image.height;

    ctx.drawImage(
        image,
        0,
        0
    );

    console.log(
        canvas.width,
        canvas.height
    );
};

let startX;
let startY;

let currentX;
let currentY;

let drawing = false;

let rois = [];

// =========================================================================
// EDITED SECTION START: INTERACTIVE SCALING RATIO MOUSE TRACKING
// =========================================================================

// Detect Mouse Press 
canvas.addEventListener("mousedown", (event) => {

    const rect = canvas.getBoundingClientRect();

    // Map screen display bounds to original absolute pixel buffer context structures
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    startX = (event.clientX - rect.left) * scaleX;
    startY = (event.clientY - rect.top) * scaleY;

    drawing = true;

    console.log(
        event.clientX,
        event.clientY
    );
    
    console.log(
        startX,
        startY
    );
    
});

// Detect Dragging 
canvas.addEventListener("mousemove", (event) => {

    if (!drawing) return;

    const rect = canvas.getBoundingClientRect();

    // Multiply structural coordinates offset alignment variables
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    currentX = (event.clientX - rect.left) * scaleX;
    currentY = (event.clientY - rect.top) * scaleY;

    //redrawCanvas();
    redrawAllROIs();

    drawRectangle(
        startX,
        startY,
        currentX,
        currentY,
        "red"
    );
});

// Detect Mouse Release 
canvas.addEventListener("mouseup", (event) => {

    drawing = false;

    const rect = canvas.getBoundingClientRect();

    // Normalize final bounds configurations array matching scaling context profiles
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    currentX = (event.clientX - rect.left) * scaleX;
    currentY = (event.clientY - rect.top) * scaleY;

    const roiName = prompt( "Enter ROI Name:" );

    const x =
        Math.min(startX, currentX);

    const y =
        Math.min(startY, currentY);

    const width =
        Math.abs(currentX - startX);

    const height =
        Math.abs(currentY - startY);

    const roi = {

        id: Date.now(),

        name: roiName || `ROI ${rois.length + 1}`,

        x: x / canvas.width,

        y: y / canvas.height,

        width: width / canvas.width,

        height: height / canvas.height
    };

    rois.push(roi);

    console.log(roi);

    //redrawCanvas();
    redrawAllROIs();

    //update the ROI list
    updateROIList();

    drawRectangle(
        roi.x * canvas.width,
        roi.y * canvas.height,
        (roi.x + roi.width) * canvas.width,
        (roi.y + roi.height) * canvas.height,
        "red",
        roi.name
    );
});

// =========================================================================
// EDITED SECTION END: SCALING BALANCING FINISHED
// =========================================================================

// event for loading existing rois for a particular image or lab
window.addEventListener("load", loadROIs);

// Draw Rectangle Function 
function drawRectangle(
    x1,
    y1,
    x2,
    y2,
    color,
    label=""
){

    ctx.strokeStyle = color;

    ctx.lineWidth = 3;

    ctx.strokeRect(

        Math.min(x1, x2),

        Math.min(y1, y2),

        Math.abs(x2 - x1),

        Math.abs(y2 - y1)

    );

    ctx.font = "18px Arial";

    ctx.fillStyle = color;

    ctx.fillText(
        label,
        Math.min(x1, x2),
        Math.min(y1, y2) - 5
    );
}

// Redraw Function 
function redrawCanvas(){

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    ctx.drawImage(
        image,
        0,
        0
    );
}

// Redraw Function for multiple ROI 
function redrawAllROIs(){

    redrawCanvas();

    rois.forEach(roi => {

        // coordinate adaptation
        const x =
            roi.x * canvas.width;

        const y =
            roi.y * canvas.height;

        const width =
            roi.width * canvas.width;

        const height =
            roi.height * canvas.height;

        drawRectangle(
            x,
            y,
            x + width,
            y + height,
            "red",
            roi.name
        );

    });
}

// update the roi list with stylized Tailwind components feed
function updateROIList(){

    const list =
        document.getElementById("roiList");

    list.innerHTML = "";

    rois.forEach(roi => {

        const li =
            document.createElement("li");
        
        li.className = "bg-white p-3 rounded-lg border border-slate-200 shadow-sm flex items-center justify-between group hover:border-slate-300 transition-all text-xs";

        li.innerHTML = `
            <div class="flex flex-col gap-0.5">
                <span class="font-bold text-slate-700">${roi.name}</span>
                <span class="text-[10px] text-slate-400 font-mono">
                    X: ${Math.round(roi.x * canvas.width)}, 
                    Y: ${Math.round(roi.y * canvas.height)}, 
                    W: ${Math.round(roi.width * canvas.width)}, 
                    H: ${Math.round(roi.height * canvas.height)}
                </span>
            </div>
            <button onclick="deleteROI(${roi.id})" class="text-slate-400 hover:text-red-500 p-1 rounded transition-colors font-sans font-medium text-xs">
                Delete
            </button>
        `;

        list.appendChild(li);

    });
}

// function for loading existing rois
async function loadROIs(){

    try{

        const response =
            await fetch(
                `http://localhost:5000/api/roi/${currentLabId}`
            );

        const data =
            await response.json();

        rois = data;

        redrawAllROIs();

        updateROIList();


    }

    catch(error){

        console.error(error);

    }

}

// function for deleting a roi
function deleteROI(id){

    rois = rois.filter(

        roi => roi.id !== id

    );

    redrawAllROIs();

    updateROIList();
}
window.deleteROI = deleteROI;

// #######  To save roi  ####### 
document
.getElementById("saveBtn")
.addEventListener("click", saveROI);

// Save Function  
async function saveROI(){

    try{

        const response = await fetch(
            "http://localhost:5000/api/roi",
            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body: JSON.stringify({

                    r_lab_id: currentLabId,

                    rois: rois
                })

            }
        );

        const result = await response.json();

        alert(result.message);

    }
    catch(error){

        console.error(error);

        alert("Failed to save ROI");
    }
}
*/