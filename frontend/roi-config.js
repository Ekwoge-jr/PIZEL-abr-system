const canvas = document.getElementById("roiCanvas");
const ctx = canvas.getContext("2d");
const container = document.getElementById("container");


const image = new Image();


{/** image path */}
image.src = "./images/test_image.png";

{/** image loading */}
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



{/** Detect Mouse Press */}
canvas.addEventListener("mousedown", (event) => {

    const rect = canvas.getBoundingClientRect();

    startX = event.clientX - rect.left;
    startY = event.clientY - rect.top;

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




{/** Detect Dragging */}
canvas.addEventListener("mousemove", (event) => {

    if (!drawing) return;

    const rect = canvas.getBoundingClientRect();

    currentX = event.clientX - rect.left;
    currentY = event.clientY - rect.top;

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





{/** Detect Mouse Release */}
canvas.addEventListener("mouseup", (event) => {

    drawing = false;

    const rect = canvas.getBoundingClientRect();

    currentX = event.clientX - rect.left;
    currentY = event.clientY - rect.top;

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

        //name: `ROI ${rois.length + 1}`,
        name: roiName || `ROI ${rois.length + 1}`,


        x: x / canvas.width,

        y: y / canvas.height,

        width: width / canvas.width,

        height: height / canvas.height


        /** 
        x: Math.round(
            Math.min(startX, currentX)
        ),

        y: Math.round(
            Math.min(startY, currentY)
        ),

        width: Math.round(
            Math.abs(currentX - startX)
        ),

        height: Math.round(
            Math.abs(currentY - startY)
        )
        */
    };

    rois.push(roi);


    console.log(roi);

    //redrawCanvas();
    redrawAllROIs();

    //update the ROI list
    updateROIList();


    drawRectangle(
        roi.x,
        roi.y,
        roi.x + roi.width,
        roi.y + roi.height,
        "red",
        roi.name
    );
});



// event for loading existing rois for a particular image or lab
window.addEventListener("load", loadROIs);



{/** Draw Rectangle Function */}
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
        x1,
        y1 - 5
    );
}



{/** Redraw Function */}
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



{/** Redraw Function for multiple ROI */}
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

            //roi.x,
            //roi.y,
            //roi.x + roi.width,
            //roi.y + roi.height,

            x,

            y,

            x + width,

            y + height,

            "red",

            roi.name
        );

    });
}



// update the roi list
function updateROIList(){

    const list =
        document.getElementById("roiList");

    list.innerHTML = "";

    rois.forEach(roi => {

        const li =
            document.createElement("li");

        li.innerHTML =
            `${roi.name}
             (${ Math.round( roi.x * canvas.width ) },
             ${ Math.round( roi.y * canvas.height ) },
             ${ Math.round( roi.width * canvas.width )},
             ${ Math.round( roi.height * canvas.height )})
             
             <button onclick="deleteROI(${roi.id})"
                style="margin-left:10px;"
             >
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
                "http://localhost:5000/api/roi/1"
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








{/** #######  To save roi  ####### */}
document
.getElementById("saveBtn")
.addEventListener("click", saveROI);



{/**  Save Function  */}
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

                    r_lab_id:1,

                    rois: rois

                    //x: roi.x,
                    //y: roi.y,

                    //width: roi.width,
                    //height: roi.height
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





/**
//########################################################
//lab creation and image/video upload
//########################################################

let currentLabId = null;

document
.getElementById("uploadForm").addEventListener(
    "submit",
    uploadLab
);

async function uploadLab(event){

    event.preventDefault();

    const formData = new FormData();

    formData.append(
        "name",
        document.getElementById("labName").value
    );

    formData.append(
        "image",
        document.getElementById("imageFile").files[0]
    );

    formData.append(
        "video",
        document.getElementById("videoFile").files[0]
    );

    try{

        const response =
            await fetch(
                "http://localhost:5000/api/labs",
                {
                    method:"POST",
                    body:formData
                }
            );

        const result = await response.json();

        currentLabId = result.lab_id;

        image.src = result.image_url;

        alert( "Upload successful" );
    }

    catch(error){
        console.error(error);
    }
} */