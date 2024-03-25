// Creates 2D arrays
let allPlates = {
  "plates": [],
  "confs": [],
  "types": [],
  "lat": [],
  'lon': [],
  "times": [],
  "paths": []
};
let passPlates = {
    "plates": [],
    "stati": []
};

let passPlatesExists = false;

// Gets certain elements
const plateDisplay = document.querySelector('.plate-text');
const statusDisplay = document.querySelector('.status-text');
const confDisplay = document.querySelector('.confidence-text');
const dateDisplay = document.querySelector('.date-text');
const imageDisplay = document.querySelector('.display-image');
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
function createPlateElement(plateIndex) {
    const plate = allPlates['plates'][plateIndex];
    const conf = allPlates['confs'][plateIndex]*100 + '%';
    const date = allPlates['times'][plateIndex];
    const path = '.' + ['paths'][plateIndex]; // Exits frontend dir and into 
    const initialStatus = testStatus(plate);
    const location = allPlates.lat[plateIndex] + ", " + allPlates.lon[plateIndex];
    const mapSource = 'https://www.google.com/maps/embed/v1/place?q=' + location + '&key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8';

   

    const plateElement = document.createElement('div');
    plateElement.classList.add('plates', 'box');
    plateElement.id = 'infobox' + plate; 
    document.getElementById('plateContainer').appendChild(plateElement);


    const subDivs = [
        { classes: ['plate-text', 'main-text'], text: plate },
        { classes: ['status-text', plate], text: initialStatus },
        { classes: ['confidence-text', 'subtext'], text: conf },
        { classes: ['date-text', 'subtext'], text: date }
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
        plateElement.style['background-color'] = '#f1f1f1';
        plateDisplay.textContent = plate;
        statusDisplay.textContent = testStatus(plate);
        confDisplay.textContent = conf;
        dateDisplay.textContent = date;
        imageDisplay.setAttribute('src', path);
        mapDisplay.setAttribute('src', mapSource);
    });



}


// Tests status of inputted plate against given list
function testStatus(plate)  {
    // ignore if 
    if(!passPlatesExists) return null;

    // FUTURE IMPROVEMENT - PRESORT LIST AND USE BINARY SEARCH
    if(passPlates.plates.indexOf(plate) >= 0) return "pass";
    return "fail";
}

function updateStatus() {
    allPlates.plates.forEach((plate, index) =>  {
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
    });
}


// Event listener for uploading CSV data
document.getElementById("uploadData").addEventListener('change', async (event) => {
    try {
        const newData = await parseCSV(event, ['plates', 'confs', 'types', 'lat', 'lon', 'times', 'paths']);
        // Iterate through the new data and create new elements for new plates
        newData['plates'].forEach((plate, index) => {
            // Skip plate if plate is already in allPlates or confidence < 60%
            if (allPlates['plates'].includes(plate) || newData.confs[index] < 0.6) return;

            Object.keys(newData).forEach(key => {
                allPlates[key] = allPlates[key].concat(newData[key][index]);
            });
            // Create a box for new plates
            createPlateElement(allPlates['plates'].length-1);
        });
    } catch (error) {
        console.error(error);
    }
});

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


