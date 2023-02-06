// Programs configuration dict
var programs = {};

document.getElementById('buttonReturn').onclick = function () {
    httpPost('/programs', programs);
    location.href = '/watering-controller';
};

function httpGet(url) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('GET', url, false); // false for synchronous request
    xmlHttp.send(null);
    return JSON.parse(xmlHttp.responseText);
}

function httpPost(url, data) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open('POST', url, false); // false for synchronous request
    xmlHttp.setRequestHeader('Content-Type', 'application/json');
    xmlHttp.send(JSON.stringify(data));
    return JSON.parse(xmlHttp.responseText);
}

window.onload = function () {
    httpGetRequestPrograms();
}

// Get programs from the backend
function httpGetRequestPrograms() {
    programs = httpGet('/programs');

    for (let id in programs){
        createProgramConsole(id, programs[id]);
    }
}

// Create the console for configure each program
function createProgramConsole(id, program) {
    var mainCol = document.getElementById('programsConsoleCol');

    var programConsoleRow = document.createElement('div');
    programConsoleRow.setAttribute('id', 'programConsoleRow' + id);
    programConsoleRow.setAttribute('class', 'row div-border my-3');
    mainCol.appendChild(programConsoleRow);

    var programConsoleCol = document.createElement('div');
    programConsoleCol.setAttribute('id', 'programConsoleCol' + id);
    programConsoleCol.setAttribute('class', 'col');
    programConsoleRow.appendChild(programConsoleCol);

    var titleRow = document.createElement('div');
    titleRow.setAttribute('class', 'row justify-content-between py-3');
    programConsoleCol.appendChild(titleRow);

    var titleCol = document.createElement('div');
    titleCol.setAttribute('class', 'col-auto');
    titleRow.appendChild(titleCol);

    var titleH = document.createElement('h2');
    titleH.innerText = 'Programa ' + id;
    titleCol.appendChild(titleH);

    var configRow = document.createElement('div');
    configRow.setAttribute('id', 'programConsoleConfigRow' + id);
    configRow.setAttribute('class', 'row pb-3');
    programConsoleCol.appendChild(configRow);

    createDaysStartsConfig(id, program);
    createCircuitsConfig(id, program['circuits']);
}

// Create the structure for the starts, weekdays and activate buttons
function createDaysStartsConfig(idx, program) {
    var mainRow = document.getElementById('programConsoleConfigRow' + idx);

    var configCol = document.createElement('div');
    configCol.setAttribute('id', 'programConsoleConfigDaysStartsCol' + idx);
    configCol.setAttribute('class', 'col-3 col-md-4');
    mainRow.appendChild(configCol);

    for (let index = 1; index <= Object.keys(program['starts']).length; index++) {
        var startHourRow = document.createElement('div');
        startHourRow.setAttribute('class', 'row justify-content-start');
        configCol.appendChild(startHourRow);

        var startHourCol = document.createElement('div');
        startHourCol.setAttribute('class', 'col');
        startHourRow.appendChild(startHourCol);

        var inputGroupDiv = document.createElement('div');
        inputGroupDiv.setAttribute('class', 'input-group mb-3');
        startHourCol.appendChild(inputGroupDiv);

        var inputGroupButtonDiv = document.createElement('div');
        inputGroupButtonDiv.setAttribute('class', 'input-group-prepend');
        inputGroupDiv.appendChild(inputGroupButtonDiv);

        var inputGroupButton = document.createElement('button');
        if (program['starts'][index]['activated']) {
            inputGroupButton.setAttribute('class', 'btn btn-secondary');
        } else {
            inputGroupButton.setAttribute('class', 'btn btn-outline-secondary');
        }
        inputGroupButton.setAttribute('type', 'button');
        inputGroupButton.setAttribute('id', 'program' + idx + 'start' + index + 'button');
        inputGroupButton.onclick = function() {startsButtonOnClick(idx, index)};
        inputGroupButton.innerText = 'Hora inicio ' + index;
        inputGroupButtonDiv.appendChild(inputGroupButton);

        var inputGroupInput = document.createElement('input');
        inputGroupInput.setAttribute('class', 'form-control');
        inputGroupInput.setAttribute('type', 'text');
        inputGroupInput.setAttribute('aria-describedby', 'basic-addon1');
        inputGroupInput.setAttribute('id', 'program' + idx + 'start' + index + 'input');
        inputGroupInput.oninput = function() {startsButtonOnInput(idx, index)};
        inputGroupInput.placeholder = 'HH:MM';
        inputGroupInput.value = program['starts'][index]['hour'];
        inputGroupDiv.appendChild(inputGroupInput);
    }

    var daysRow = document.createElement('div');
    daysRow.setAttribute('class', 'row justify-content-center');
    configCol.appendChild(daysRow);

    var daysCol = document.createElement('div');
    daysCol.setAttribute('class', 'col-auto py-2');
    daysRow.appendChild(daysCol);

    var toolbarDiv = document.createElement('div');
    toolbarDiv.setAttribute('class', 'btn-toolbar');
    toolbarDiv.setAttribute('role', 'toolbar');
    daysCol.appendChild(toolbarDiv);

    var buttonsGroupDiv = document.createElement('div');
    buttonsGroupDiv.setAttribute('class', 'btn-group mr-2');
    buttonsGroupDiv.setAttribute('role', 'group');
    toolbarDiv.appendChild(buttonsGroupDiv);

    days_str = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
    days_str.forEach(function (item, index) {
        var buttonDay = document.createElement('div');
        if (program['days'][item]) {
            buttonDay.setAttribute('class', 'btn btn-secondary');
        } else {
            buttonDay.setAttribute('class', 'btn btn-outline-secondary');
        }
        buttonDay.setAttribute('type', 'button');
        buttonDay.setAttribute('id', 'program' + idx + 'day' + item + 'button');
        buttonDay.onclick = function() {daysButtonOnClick(idx, item)};
        buttonDay.innerText = item;
        buttonsGroupDiv.appendChild(buttonDay);
    });

    var activateRow = document.createElement('div');
    activateRow.setAttribute('class', 'row justify-content-center');
    configCol.appendChild(activateRow);

    var activateCol = document.createElement('div');
    activateCol.setAttribute('class', 'col py-4');
    activateRow.appendChild(activateCol);

    var buttonActivate = document.createElement('div');
    buttonActivate.setAttribute('type', 'button');
    buttonActivate.setAttribute('style', 'width: 100%;');
    buttonActivate.setAttribute('id', 'program' + idx + 'activatebutton');
    buttonActivate.onclick = function() {activateButtonOnClick(idx)};
    if (program['selected']) {
        buttonActivate.setAttribute('class', 'btn btn-secondary');
        buttonActivate.innerText = 'Desactivar';
    } else {
        buttonActivate.setAttribute('class', 'btn btn-outline-secondary');
        buttonActivate.innerText = 'Activar';
    }
    activateCol.appendChild(buttonActivate);
}

// Create the structure for the circuits buttons
function createCircuitsConfig(idx, circuits) {
    var mainRow = document.getElementById('programConsoleConfigRow' + idx);

    var configCol = document.createElement('div');
    configCol.setAttribute('id', 'programConsoleConfigCircuitsCol' + idx);
    configCol.setAttribute('class', 'col');
    mainRow.appendChild(configCol);

    var auxRow = document.createElement('div');
    auxRow.setAttribute('class', 'row justify-content-end');
    configCol.appendChild(auxRow);

    const maxRowCircuits = 6;
    n_cols = Object.keys(circuits).length / maxRowCircuits;
    for (let i = 0; i < n_cols; i++){
        var auxCol = document.createElement('div');
        auxCol.setAttribute('class', 'col-4');
        auxRow.appendChild(auxCol);

        for (let nCircuits = 1; nCircuits <= maxRowCircuits; nCircuits++) {
            let circuitId = nCircuits + (i * maxRowCircuits);
            var circuit = circuits[circuitId];
            
            inputRow = document.createElement('div');
            inputRow.setAttribute('class', 'row');
            auxCol.appendChild(inputRow);

            inputCol = document.createElement('div');
            inputCol.setAttribute('class', 'col-10');
            inputRow.appendChild(inputCol);

            inputDiv = document.createElement('div');
            inputDiv.setAttribute('class', 'input-group mb-3');
            inputCol.appendChild(inputDiv);

            idDiv = document.createElement('div');
            idDiv.setAttribute('class', 'input-group-prepend');
            inputDiv.appendChild(idDiv);

            var buttonCircuit = document.createElement('div');
            buttonCircuit.setAttribute('type', 'button');
            buttonCircuit.setAttribute('id', 'program' + idx + 'circuit' + circuitId + 'button');
            buttonCircuit.onclick = function() {circuitsButtonOnClick(idx, circuitId)};
            buttonCircuit.innerText = circuitId;
            if (circuit['activated']) {
                buttonCircuit.setAttribute('class', 'btn btn-secondary');
            } else {
                buttonCircuit.setAttribute('class', 'btn btn-outline-secondary');
            }
            idDiv.appendChild(buttonCircuit);

            var timeInput = document.createElement('input');
            timeInput.setAttribute('class', 'form-control');
            // timeInput.setAttribute('type', 'number');
            // timeInput.setAttribute('min', '0');
            // timeInput.setAttribute('step', '1');
            // timeInput.placeholder = '0';
            timeInput.setAttribute('id', 'program' + idx + 'circuit' + circuitId + 'input');
            timeInput.oninput = function() {circuitsButtonOnInput(idx, circuitId)};
            timeInput.value = circuit['time'];
            inputDiv.appendChild(timeInput);

            unitsDiv = document.createElement('div');
            unitsDiv.setAttribute('class', 'input-group-append');
            inputDiv.appendChild(unitsDiv);

            var unitsSpan = document.createElement('span');
            unitsSpan.setAttribute('class', 'input-group-text');
            unitsSpan.innerText = 'mins';
            unitsDiv.appendChild(unitsSpan);
        }
    }
}

// Function to be executed when a start button is clicked
function startsButtonOnClick(programId, startId) {
    var input = document.getElementById('program' + programId + 'start' + startId + 'input');
    if ((programs[programId]['starts'][startId]['hour'] == '') & (!programs[programId]['starts'][startId]['activated'])){
        input.setAttribute('style', 'border-color: red; box-shadow: 0 0 0 0.2rem rgb(255 0 0 / 25%);');
    } else {
        input.removeAttribute('style');
        programs[programId]['starts'][startId]['activated'] = !programs[programId]['starts'][startId]['activated'];
        var button = document.getElementById('program' + programId + 'start' + startId + 'button');
        if (programs[programId]['starts'][startId]['activated']) {
            button.removeAttribute('class');
            button.setAttribute('class', 'btn btn-secondary');
        } else {
            button.removeAttribute('class');
            button.setAttribute('class', 'btn btn-outline-secondary');
        }
    }
}

// Function to be executed when a start input is filled
function startsButtonOnInput(programId, startId) {
    var input = document.getElementById('program' + programId + 'start' + startId + 'input');
    var input_val = input.value;
    if ((/^([01][0-9]|2[0-3]):([0-5][0-9])$/.test(input_val)) || (input_val == '')) {
        programs[programId]['starts'][startId]['hour'] = input_val;
        input.removeAttribute('style');
    } else {
        input.setAttribute('style', 'border-color: red; box-shadow: 0 0 0 0.2rem rgb(255 0 0 / 25%);');
    }
}

// Function to be executed when a activate button is clicked
function activateButtonOnClick(programId) {
    programs[programId]['selected'] = !programs[programId]['selected'];
    var button = document.getElementById('program' + programId + 'activatebutton');
    if (programs[programId]['selected']) {
        button.removeAttribute('class');
        button.setAttribute('class', 'btn btn-secondary');
        button.innerText = 'Desactivar';
    } else {
        button.removeAttribute('class');
        button.setAttribute('class', 'btn btn-outline-secondary');
        button.innerText = 'Activar';
    }
}

// Function to be executed when a day button is clicked
function daysButtonOnClick(programId, day) {
    programs[programId]['days'][day] = !programs[programId]['days'][day];
    var button = document.getElementById('program' + programId + 'day' + day + 'button');
    if (programs[programId]['days'][day]) {
        button.removeAttribute('class');
        button.setAttribute('class', 'btn btn-secondary');
    } else {
        button.removeAttribute('class');
        button.setAttribute('class', 'btn btn-outline-secondary');
    }
}

// Function to be executed when a circuit button is clicked
function circuitsButtonOnClick(programId, circuitId) {
    programs[programId]['circuits'][circuitId]['activated'] = !programs[programId]['circuits'][circuitId]['activated'];
    var button = document.getElementById('program' + programId + 'circuit' + circuitId + 'button');
    if (programs[programId]['circuits'][circuitId]['activated']) {
        button.removeAttribute('class');
        button.setAttribute('class', 'btn btn-secondary');
    } else {
        button.removeAttribute('class');
        button.setAttribute('class', 'btn btn-outline-secondary');
    }
}

// Function to be executed when a circuit input is filled
function circuitsButtonOnInput(programId, circuitId) {
    var input = document.getElementById('program' + programId + 'circuit' + circuitId + 'input');
    var input_val = input.value;
    if ((/^[0-9]\d*$/.test(input_val)) || (input_val == '')) {
        if (input_val == '') {
            programs[programId]['circuits'][circuitId]['time'] = 0;
        } else {
            programs[programId]['circuits'][circuitId]['time'] = parseInt(input_val);
        }
        input.removeAttribute('style');
    } else {
        input.setAttribute('style', 'border-color: red; box-shadow: 0 0 0 0.2rem rgb(255 0 0 / 25%);');
    }
}