// Time to execute each circuit in a manual execution
var circuitsTime = 0;

// Socket.io initialization
console.log(window.location.href);
var socket = io(window.location.href);

// Socket.io connect receiver
socket.on('connect', function () {
    console.log("Websocket connected...!", socket.connected)
});

// Socket.io connect error receiver
socket.on('connect_error', (err) => {
    console.log(`connect_error due to ${err.message}`);
});

// Socket.io programs activation feedback receiver
socket.on('activated-programs', function (data) {
    console.log(data);
    if (data['activated']) {
        hideCancelButton(false);
        lockAllButtons(true);
        clearAllProgramsButtons();
        programButtonActivated(data['program']);
    } else {
        clearAllProgramsButtons();
        lockAllButtons(false);
        hideCancelButton(true);
    }
});

// Socket.io circuits activation feedback receiver
socket.on('activated-circuits', function (data) {
    console.log(data);
    // {'circuit': idx, 'activated': False, 'min': mins}
    if (data['activated']) {
        hideCancelButton(false);
        lockAllButtons(true);
        clearAllCircuitsButtons();
        circuitButtonActivated(data['circuit']);
        modifyMinsInput(data['mins']);
    } else {
        clearAllCircuitsButtons();
        lockAllButtons(false);
        modifyMinsInput('');
        hideCancelButton(true);
    }
});

// Socket.io programs activation feedback receiver
socket.on('cancell-all', function (data) {
    clearAllProgramsButtons();
    lockAllButtons(false);
    clearAllCircuitsButtons();
    modifyMinsInput('');
    hideCancelButton(true);
});

function httpGet(url, async=false) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', url, async); // false for synchronous request
    xmlHttp.send(null);
    if (xmlHttp.responseText) {
        return JSON.parse(xmlHttp.responseText);
    }
}

window.onload = function () {
    displayDate();
    httpGetRequestPrograms();
    httpGetRequestNCircuits();
}

setInterval(displayDate, 1000);

function displayDate() {
    current_date = new Date();

    year = current_date.getFullYear();
    month = current_date.getMonth() + 1;
    month = ((month < 10) ? '0' + month : month);
    day = current_date.getDate();
    day = ((day < 10) ? '0' + day : day);
    hour = current_date.getHours();
    hour = ((hour < 10) ? '0' + hour : hour);
    minute = current_date.getMinutes();
    minute = ((minute < 10) ? '0' + minute : minute);

    document.getElementById('dateTime').innerHTML = year + "/" + month + "/" + day + "  " + hour + ":" + minute;
}

// function updateInfo() {
//     var info = httpGet('/info');
    
//     displayDate(info['datetime']);
    
//     // if (Object.keys(info['onprogress']).length != 0) {
//     //     lockAllButtons(true);
//     // } else {
//     //     lockAllButtons(false);
//     // }

// }

// function displayDate(datetime) {
//     document.getElementById('dateTime').innerHTML = datetime;
// }

// Request programs configuration from backend
function httpGetRequestPrograms() {
    var programs = httpGet('/programs')

    for (let id in programs){
        createProgramTableRow(id, programs[id]);
    }
}

// Create each row of the programs table from programs config
function createProgramTableRow(id, program) {
    var tableBody = document.getElementById('programsTable');

    var tableRow = document.createElement('tr');
    tableBody.appendChild(tableRow);
    
    var cellButton = document.createElement('th');
    cellButton.setAttribute('scope', 'row');
    cellButton.setAttribute('align', 'center');
    tableRow.appendChild(cellButton);

    var idButton = document.createElement('button');
    idButton.setAttribute('id', 'buttonProgram' + id);
    idButton.setAttribute('type', 'button');
    idButton.setAttribute('class', 'btn btn-outline-primary');
    idButton.onclick = function() {programButtonOnClick(id)};
    idButton.innerHTML = id;
    cellButton.appendChild(idButton);

    var cellDays = document.createElement('td');
    cellDays.setAttribute('class', 'align-middle');
    cellDays.setAttribute('align', 'center');
    days = [];
    days_str = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
    days_str.forEach(function (day, index) {
        if (program['days'][day]) {
            days.push(day);
        } 
    });
    cellDays.innerHTML = ((days.length > 0) ? days.join(' | ') : '-');
    tableRow.appendChild(cellDays);

    var cellStarts = document.createElement('td');
    cellStarts.setAttribute('class', 'align-middle');
    cellStarts.setAttribute('align', 'center');
    starts = [];
    for (const [startId, startInfo] of Object.entries(program['starts'])) {
        if (startInfo['activated']) {
            starts.push(startInfo['hour']);
        } 
    }
    cellStarts.innerHTML = ((starts.length > 0) ? starts.join(' | ') : '-');
    tableRow.appendChild(cellStarts);

    var cellTime = document.createElement('td');
    cellTime.setAttribute('class', 'align-middle');
    cellTime.setAttribute('align', 'center');
    totalTime = 0;
    for (const [circuitId, circuitInfo] of Object.entries(program['circuits'])) {
        if (circuitInfo['activated']) {
            totalTime = totalTime + parseInt(circuitInfo['time']);
        } 
    }
    cellTime.innerHTML = ((totalTime > 0) ? totalTime : '-');
    tableRow.appendChild(cellTime);

    var cellCircuits = document.createElement('td');
    cellCircuits.setAttribute('class', 'align-middle');
    cellCircuits.setAttribute('align', 'center');
    circuits = [];
    for (const [circuitId, circuitInfo] of Object.entries(program['circuits'])) {
        if (circuitInfo['activated']) {
            circuits.push(circuitId);
        } 
    }
    cellCircuits.innerHTML = ((circuits.length > 0) ? circuits.join(' | ') : '-');
    tableRow.appendChild(cellCircuits);

    var cellActive = document.createElement('td');
    cellActive.setAttribute('class', 'align-middle');
    cellActive.setAttribute('align', 'center');
    tableRow.appendChild(cellActive);

    var activeIcon = document.createElement('i');
    if (program['selected']) {
        activeIcon.setAttribute('class', 'bi bi-check-circle green-check');
    } else {
        activeIcon.setAttribute('class', 'bi bi-x-circle red-cross');
    }
    cellActive.appendChild(activeIcon);

}

// Request the number of circuits from the backend and create the buttons
function httpGetRequestNCircuits() {
    // TO-DO: Get the number of circuits from backend

    var buttonsDiv = document.getElementById('circuitsButtonsDiv');

    for (let id = 1; id <= 12; id++) {
        var idButton = document.createElement('button');
        idButton.setAttribute('id', 'buttonCircuit' + id);
        idButton.setAttribute('type', 'button');
        idButton.setAttribute('class', 'btn btn-outline-primary');
        idButton.onclick = function() {circuitButtonOnClick(id)};
        idButton.innerHTML = id;
        buttonsDiv.appendChild(idButton);
    }
}

// Function to be executed when a circuit input is filled
function circuitsTimeOnInput() {
    var input = document.getElementById('inputCircuitsTime');
    var input_val = input.value;
    if ((/^[0-9]\d*$/.test(input_val)) || (input_val == '')) {
        if (input_val == '') {
            circuitsTime = 0;
        } else {
            circuitsTime = parseInt(input_val);
        }
        input.removeAttribute('style');
    } else {
        input.setAttribute('style', 'border-color: red; box-shadow: 0 0 0 0.2rem rgb(255 0 0 / 25%);');
    }
}

// Function to be executed when a program button is clicked
function programButtonOnClick(id) {
    httpGet('/program/' + id, async=true);
}

// Change style from a program button to show it ativated 
function programButtonActivated(id) {
    var button = document.getElementById('buttonProgram' + id);
    button.removeAttribute('class');
    button.setAttribute('class', 'btn btn-primary');
}

// Function to be executed when a circuit button is clicked
function circuitButtonOnClick(id) {
    httpGet('/circuit/' + id + '/' + circuitsTime, async=true);
}

// Change style from a circuit button to show it ativated 
function circuitButtonActivated(id) {
    var button = document.getElementById('buttonCircuit' + id);
    button.removeAttribute('class');
    button.setAttribute('class', 'btn btn-primary');
}

// Modify the content of the minutes input to update it
function modifyMinsInput(mins) {
    var input = document.getElementById('inputCircuitsTime');
    input.value = mins;
    circuitsTime = mins;
}

// Change style of all programs buttons to show them deactivated
function clearAllProgramsButtons() {
    var programsTableBody = document.getElementById('programsTable');
    for (let id = 1; id <= (programsTableBody.childNodes.length - 3); id++) {
        var button = document.getElementById('buttonProgram' + id);
        button.removeAttribute('class');
        button.setAttribute('class', 'btn btn-outline-primary');
    }
} 

// Change style of all circuits buttons to show them deactivated
function clearAllCircuitsButtons() {
    var circuitsButtonsDiv = document.getElementById('circuitsButtonsDiv');
    for (let id = 1; id <= (circuitsButtonsDiv.childNodes.length - 3); id++) {
        var button = document.getElementById('buttonCircuit' + id);
        button.removeAttribute('class');
        button.setAttribute('class', 'btn btn-outline-primary');
    }
}

// Disable all buttons
function lockAllButtons(lock) {
    var button = document.getElementById('buttonEditPrograms');
    button.disabled = lock;
    
    var input = document.getElementById('inputCircuitsTime');
    input.disabled = lock;

    var programsTableBody = document.getElementById('programsTable');
    for (let id = 1; id <= (programsTableBody.childNodes.length - 3); id++) {
        var button = document.getElementById('buttonProgram' + id);
        button.disabled = lock;
    }

    var circuitsButtonsDiv = document.getElementById('circuitsButtonsDiv');
    for (let id = 1; id <= (circuitsButtonsDiv.childNodes.length - 3); id++) {
        var button = document.getElementById('buttonCircuit' + id);
        button.disabled = lock;
    }
}

// Function to be executed when cancel button is clicked
function cancelButtonOnClick() {
    hideCancelButton(true);
    httpGet('/cancel');
}

// Hide or show cancel button
function hideCancelButton(hide) {
    var button = document.getElementById('cancelButton');
    button.hidden = hide;
}

document.getElementById('buttonEditPrograms').onclick = function () {
    location.href = '/watering-controller-edit-programs';
};
