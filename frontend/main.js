const socket = io('http://<YOUR_NODEJS_SERVER_IP>:3000');
const imageDisplay = document.querySelector('.display-image');

document.getElementById('startButton').addEventListener('click', function() {
    if(passPlatesExists)    {
        socket.send('toggleCapture');
        document.getElementById('startButton').style['background-color'] = 'gray';
    }   else    {
        console.log('Upload a reference first!');
    }
});


socket.on('plateRead', (plate) => {
    createPlateElement(plate);
});


let passPlates = {
    "plates": [],
    "stati": []
};

let passPlatesExists = false;
let prevDisplayPlate = null;

// Gets certain elements
const plateDisplay = document.querySelector('.plate-text');
const statusDisplay = document.querySelector('.status-text');
const confDisplay = document.querySelector('.confidence-text');
const dateDisplay = document.querySelector('.date-text');
const mapDisplay = document.querySelector('iframe.map');

// Function to parse CSV files
function parseCSV(event, keys) {
    return new Promise((resolve, reject) => {
        let data = {};
        const files = event.target.files;
        if (files.length == 0) return reject('No files selected');
        const file = files[0];
        if (!file.name.toLowerCase().endsWith('csv')) {
            return reject('File is not a CSV');
        }
        const reader = new FileReader();
        reader.onload = function (e) {
            const text = e.target.result;
            const rows = text.split('\n');

            // Initialize data object with keys
            keys.forEach(key => {
                data[key] = [];
            });

            // Parse CSV rows
            // essentially reversing horizontal and vertical axes from CSV to data array
            rows.forEach(row => {
                const rowData = row.split(',').map(value => value.trim());
                keys.forEach((key, index) => {
                    data[key].push(rowData[index]);
                });
            });

            resolve(data); // Resolve the Promise with the parsed data
        };
        reader.readAsText(file);
    });
}

// Function to create a box displaying information for a given license plate
// plateIndex - index of a given plate's data in allPlates
function createPlateElement(plate) {
    const initialStatus = testStatus(plate);
    const location = plate.lat + ", " + plate.lon;
    const mapSource = 'https://www.google.com/maps/embed/v1/place?q=' + location + '&key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8';

   

    const plateElement = document.createElement('div');
    plateElement.classList.add('plates', 'box');
    plateElement.id = 'infobox' + plate.plateText; 
    document.getElementById('plateContainer').appendChild(plateElement);


    const subDivs = [
        { classes: ['plate-text', 'main-text'], text: plate.plateText },
        { classes: ['status-text', plate], text: initialStatus },
        { classes: ['confidence-text', 'subtext'], text: plate.score},
        { classes: ['date-text', 'subtext'], text: "3/25/24"}
    ];
    
    // Loop through the subDivs array and create each sub-div
    subDivs.forEach(subDiv => {
        console.log(plateElement instanceof Node);
        const subDivElement = document.createElement('div');
        for(i = 0; i < subDiv.classes.length; i++) {
            subDivElement.classList.add(subDiv.classes[i]);
        }
        subDivElement.textContent = subDiv.text;
        plateElement.appendChild(subDivElement); // Append each sub-div to the plate element
    });

    plateElement.addEventListener('click', () =>    {
        prevDisplayPlate.style['background-color'] = "#1f1f28"
        plateElement.style['background-color'] = '#f1f1f1';
        plateDisplay.textContent = plate.plateText;
        statusDisplay.textContent = plate.status;
        confDisplay.textContent = plate.score;
        dateDisplay.textContent = "3/25/2024";
        imageDisplay.setAttribute('src', plate.image);
        mapDisplay.setAttribute('src', mapSource);
        prevDisplayPlate = plateElement;
    });



}


// Tests status of inputted plate against given list
function testStatus(plate)  {
    // ignore if 
    if(!passPlatesExists) return null;

    // FUTURE IMPROVEMENT - PRESORT LIST AND USE BINARY SEARCH
    if(passPlates.plates.indexOf(plate.plateText) >= 0) return "pass";
    return "fail";
}

function updateStatus() {
    console.log('try again later');
    /*allPlates.plates.forEach((plate, index) =>  {
        const plateStatusBox = document.querySelector('.status-text.' + plate);
        plateStatusBox.textContent = testStatus(plate);
        plateStatusBox.style['opacity'] = '1';
        statusDisplay.style['opacity'] = '1';
        switch(plateStatusBox.textContent)   {
            case null: 
                plateStatusBox.style['background-color'] = "yellow";
                break;
            case "pass":
                plateStatusBox.style['background-color'] = "green";
                break;
            case "fail":
                plateStatusBox.style['background-color'] = "red";
                break;
            default:
                plateStatusBox.style['background-color'] = "pink";
                break;
        }
    });*/
}



// Event listener for uploading comparison data
document.getElementById('uploadCompare').addEventListener('change', async (event) => {
    try {
        // FUTURE IMPROVEMENT - Presort passPlates 
        passPlates = await parseCSV(event, ['plates', 'status']);
        console.log(passPlates);
        passPlatesExists = true;
        updateStatus();
    } catch (error) {
        console.error(error);
    }
});


