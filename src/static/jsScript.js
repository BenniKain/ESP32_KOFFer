import datajson from '/json/data.json' assert {type: 'json'};
import espjson from '/json/customespconfig.json' assert {type: 'json'};
import networksjson from '/json/customnetworks.json' assert {type: 'json'};
import boardconfjson from '/json/customboardconfig.json' assert {type: 'json'};
import ventilqueuejson from '/json/ventilqueue.json' assert {type: 'json'};
import headersjson from '/json/customheaders.json' assert {type: 'json'};


let espDict = espjson["known_ESP"];
let dataDict = datajson 
let networkDict = networksjson["known_networks"];
let pinsDict = boardconfjson["esp32"];
let ventilqueue = ventilqueuejson["ventilqueue"]

class relForm {
    constructor(paroptions, relayoptions) {
        // this.container = document.getElementById("relayform")
        this.form = document.getElementById("relayform")

        let parSelect = this.createoptions(paroptions, "Parameter")
        let ventilSelect = this.createoptions(relayoptions, "Ventil")
        let newMeas = document.getElementById("showrelayform")
        newMeas.addEventListener("click", this.show)

        // .appendChild(parOptions)// this.form.addEventListener("click", this.changeZustand)
    }
    createoptions = (optlist, parentID) => {
        let parameter = document.getElementById(parentID)
        for (let i = 0; i < optlist.length; i++) {
            let p = document.createElement("option")
            p.value = optlist[i]
            // p.name = optlist[i]
            p.innerHTML = p.value
            p.id = parentID + " option " + i
            parameter.appendChild(p)
        }
    }
    show = () => {
        if (this.form.style.display == "none") {
            this.form.style.display = "initial";
        }
        else {
            this.form.style.display = "none";
        }
    }
}

class Tabelle {
    constructor(data, headers, container) {
        this.containerID = container
        this.container = document.getElementById(container)
        this.addTable()
        this.addHeader(headers)
        this.addBody(data)
        let showLink = document.getElementById("show" + container)
        showLink.addEventListener("click", this.show)
        this.show()
    }
    show = () => {
        if (this.container.style.display == "none") {
            this.container.style.display = "";
        }
        else {
            this.container.style.display = "none"
        }
    }
    addBody = (data) => {
        let theBody = document.createElement("tbody");
        theBody.id = this.containerID + "_tbody"
        this.table.appendChild(theBody)
        //wenn daten List sind dann
        if (Array.isArray(data)) {
            this.addRowsList(data, theBody.id)
        }
        else {
            this.addRowsDict(data, theBody.id)
        }
    }
    addRowsDict = (data, parentID) => {
        let elementtypes = "td"
        for (let [k, v] of Object.entries(data)) {
            let newRow = document.createElement("tr");
            newRow.id = parentID + "_tr_" + k
            document.getElementById(parentID).appendChild(newRow)

            let tdata = document.createElement(elementtypes); //new tableelement 
            tdata.id = newRow.id + "_key_" + elementtypes + k
            tdata.innerHTML = k;                                //value in element
            newRow.appendChild(tdata);  //appendtable-element to row

            let tdata2 = document.createElement(elementtypes);
            tdata2.id = newRow.id + "_val_" + elementtypes + v
            tdata2.innerHTML = v;
            newRow.appendChild(tdata2);
        }
    }
    addRowsList = (data, parentID) => {
        let elementtypes = "td"
        for (let i = 0; i < data.length; i++) {
            let newRow = document.createElement("tr");
            newRow.id = parentID + "_tr" + i
            document.getElementById(parentID).appendChild(newRow)
            if (Array.isArray(data[0])) {
                for (let j = 0; j < data[0].length; j++) {
                    let newData = document.createElement(elementtypes)
                    newData.id = newRow.id + "_" + elementtypes + j
                    newData.innerHTML = data[i][j];
                    newRow.appendChild(newData)
                }
            }
            else {
                let newData = document.createElement(elementtypes)
                newData.id = newRow.id + "_" + elementtypes + 0
                newData.innerHTML = data[i];
                newRow.appendChild(newData)
            }
        }
    }
    addTable = () => {
        this.table = document.createElement("table");
        this.container.appendChild(this.table)
    }
    addHeader = (headers) => {
        let theheader = document.createElement("thead");
        theheader.id = this.containerID + "_thead"
        this.table.appendChild(theheader)

        let theRow = document.createElement("tr");
        theRow.id = theheader.id + "_tr"
        theheader.appendChild(theRow)

        for (let i = 0; i < headers.length; i++) {
            let tdata = document.createElement("th");
            tdata.innerHTML = headers[i];
            tdata.id = theRow.id + "_td" + i
            theRow.appendChild(tdata);
        }
    }
}

let esp = new Tabelle(espDict[3], headersjson["espHeader"], "espConfig") //[0] muss noch übergeben werden
let ventil = new Tabelle(ventilqueue, headersjson["ventilheader"], "ventilQueue") //[0] muss noch übergeben werden
let pins = new Tabelle(pinsDict["Pins"], headersjson["pinheader"], "pinConfig") //[0] muss noch übergeben werden
let netzwerk = new Tabelle(networkDict[0], headersjson["netzwerkheader"], "netzwerk") //[0] muss noch übergeben werden
let daten = new Tabelle(dataDict, headersjson["datenheader"], "daten") //[0] muss noch übergeben werden
daten.show()
let relayform = new relForm(headersjson["parOptions"], headersjson["ventilOptions"])
